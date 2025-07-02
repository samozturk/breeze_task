import pandas as pd
import sqlite3
from venue_enricher_google import search_place, get_details
from src.utils.data_loader import write_to_sqlite
import os
import json

# Load data from venues
conn = sqlite3.connect("data/venues.db")
venues_df = pd.read_sql_query("SELECT * FROM venues", conn)
conn.close()

api_key = os.environ['GOOGLE_PLACES_API_KEY']

# Enrich venues with Google Places API
dicts = []
for row in venues_df.iterrows():
    search_term = f"{row[1]["Name"]}, {row[1]["City"]}"
    search_result = search_place(place=search_term, api_key=api_key)
    details_result = get_details(place_id=search_result['place_id'], api_key=api_key)
    merged_result = {**search_result, **details_result}
    dicts.append(merged_result)

enriched_df = pd.DataFrame(dicts)

# convert your list columns to JSON strings
columns = ["photo_references", "reviews"]
for column in columns:
    enriched_df[column] = enriched_df[column].apply(json.loads)