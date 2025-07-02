import sqlite3
import pandas as pd
import random
import re
import time

class ContactFinder:
    def __init__(self, db_path='data/venues.db', use_mock_data=True):
        self.db_path = db_path
        self.use_mock_data = use_mock_data

    def add_contacts(self):
        df = self._load_enriched_venues()
        if df.empty:
            print("No enriched venues found.")
            return

        updated_records = [self._mock_find_contacts(row) for _, row in df.iterrows()]
        updated_df = pd.DataFrame(updated_records)

        self._write_updated_venues(updated_df)
        print(f"Added mock contact info to {len(updated_df)} venues and saved to 'enriched_with_contacts'.")

    def _load_enriched_venues(self):
        with sqlite3.connect(self.db_path) as conn:
            try:
                df = pd.read_sql_query("SELECT * FROM enriched_venues", conn)
                return df
            except Exception as e:
                print("Error reading enriched_venues:", e)
                return pd.DataFrame()

    def _mock_find_contacts(self, venue):
        """Append fake contact data based on existing fields."""
        time.sleep(0.05)  # Simulate delay
        venue_dict = venue.to_dict()

        name_slug = re.sub(r'\W+', '', venue_dict.get('name', '').lower())
        domain = re.sub(r'https?://(www\.)?', '', venue_dict.get('website', 'example.com')).split('/')[0]

        venue_dict['email'] = f"contact@{domain}"
        venue_dict['phone'] = f"+44 1273 {random.randint(100000, 999999)}"

        return venue_dict

    def _write_updated_venues(self, df):
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql("enriched_with_contacts", conn, if_exists="replace", index=False)
