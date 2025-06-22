import sqlite3
import pandas as pd
from jinja2 import Template
import os

class EmailGenerator:
    def __init__(self, db_path='data/venues.db', template_path='src/email/templates/outreach_template.txt'):
        self.db_path = db_path
        self.template_path = template_path

    def generate_emails(self):
        df = self._load_qualified_venues()
        if df.empty:
            print("No qualified venues found.")
            return

        template = self._load_template()
        df["email_body"] = df.apply(lambda row: self._render_email(template, row), axis=1)

        self._save_emails(df[["name", "email", "email_body"]])
        print(f"Generated emails for {len(df)} venues.")

    def _load_qualified_venues(self):
        with sqlite3.connect(self.db_path) as conn:
            try:
                df = pd.read_sql_query("SELECT * FROM qualified_venues WHERE is_qualified = 1", conn)
                if 'Name' in df.columns:
                    df = df.rename(columns={'Name': 'name'})
                return df
            except Exception as e:
                print("Error loading qualified venues:", e)
                return pd.DataFrame()

    def _load_template(self):
        with open(self.template_path, "r") as f:
            return Template(f.read())

    def _render_email(self, template, venue):
        return template.render(**venue.to_dict())

    def _save_emails(self, df):
        os.makedirs("data/output", exist_ok=True)

        # Save to text file
        with open("data/output/generated_emails.txt", "w") as f:
            for _, row in df.iterrows():
                f.write(f"---\nTo: {row['email']}\n\n{row['email_body']}\n\n")

        # Optionally also store in DB
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql("generated_emails", conn, if_exists="replace", index=False)
