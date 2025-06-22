import pandas as pd
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
import os

class VenueDistanceCalculator:
    def __init__(self, db_path='data/venues.db', table_name='venues', output_table='venues_with_distance'):
        self.db_path = db_path
        self.table_name = table_name
        self.output_table = output_table
        self.geolocator = Nominatim(user_agent="venue_analyzer")

    def get_coords(self, address):
        """
        Geocodes an address and returns its latitude and longitude coordinates.

    Args:
        address (str): The address to geocode.

        Returns:
            tuple: A tuple (latitude, longitude) if the address is found, otherwise (None, None).
        """
        try:
            location = self.geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
        return (None, None)

    def add_distance_to_city_center(self, df):
        city_centers = {}
        distances = []

        for index, row in df.iterrows():
            town = row['City']
            if town not in city_centers:
                city_centers[town] = self.get_coords(f"{town} city center")
                time.sleep(2)

        venue_coords = row['venue_coords']
        center_coords = city_centers[town]

        if venue_coords[0] and center_coords[0]:
            distance = geodesic(venue_coords, center_coords).kilometers
            distances.append(distance)
        else:
            distances.append(None)

        df['distance_to_center_km'] = distances
        return df

    def process(self):
        # Step 1: Read from SQLite
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn)

        # Step 2: Create full address for geocoding
        df['full_address'] = df['Name'] + ', ' + df['Address'] + ', ' + df['City']
        df['venue_coords'] = df['full_address'].apply(self.get_coords)
        time.sleep(2)  # To avoid hitting geocoding rate limits

        # Step 3: Calculate distance to city center
        df = self.add_distance_to_city_center(df)

        # Step 4: Write back to SQLite (new table)
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(self.output_table, conn, if_exists='replace', index=False)
        print(f"Processed {len(df)} venues and saved to '{self.output_table}' table.")

if __name__ == "__main__":
    calculator = VenueDistanceCalculator()
    calculator.process()
