import sqlite3
import pandas as pd
import random
import time
import os

class VenueEnricher:
    def __init__(self, db_path='data/venues.db', use_mock_data=True):
        self.db_path = db_path
        self.use_mock_data = use_mock_data

    def enrich_all(self):
        # Step 1: Read venues from SQLite
        df = self._load_venues()
        if df.empty:
            print("No venues found in database.")
            return

        # Step 2: Enrich each row
        enriched_records = [self._mock_enrichment(row) for _, row in df.iterrows()]
        enriched_df = pd.DataFrame(enriched_records)

        # Step 3: Write enriched data to new table
        self._write_enriched(enriched_df)
        print(f"Enriched {len(enriched_df)} venues and saved to 'enriched_venues' table.")

    def _load_venues(self):
        # TODO: use utils/data loader for this. DRY(dont repeat yourself)
        with sqlite3.connect(self.db_path) as conn:
            try:
                df = pd.read_sql_query("SELECT * FROM venues", conn)
                return df
            except Exception as e:
                print("Error loading venues table:", e)
                return pd.DataFrame()

    def _mock_enrichment(self, venue):
        """Append mock data to a venue row."""
        return {
            **venue.to_dict(),
            "website": f"https://{venue['Name'].replace(' ', '').lower()}.com",
            "description": f"{venue['Name']} is a cozy spot perfect for dates.",
            "email": f"info@{venue['Name'].replace(' ', '').lower()}.com",
            "phone": f"+44 1273 {random.randint(100000, 999999)}",
            "type": random.choice(["bar", "wine bar", "cocktail bar", "cafe", "tavern",
                                "pub", "brewery", "restaurant"]), # Can be replaced with items in the menu when I move from mock to real
            "rating": round(random.uniform(3.5, 5.0), 1),
            "review_count": random.randint(5, 150)
        }

    def _write_enriched(self, df):
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql("enriched_venues", conn, if_exists="replace", index=False)
