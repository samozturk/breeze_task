import pandas as pd
import sqlite3
import os

# Load the venues.csv
def load_venues_csv(csv_path):
    return pd.read_csv(csv_path)

# Write the DataFrame to SQLite database
def write_to_sqlite(df, db_path='../../data/venues.db', table_name='venues'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def read_from_sqlite(db_path='data/venues.db', table_name='venues'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def list_tables(db_path='data/venues.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables

# if __name__ == '__main__':
#     csv_file_path = 'data/input/venues.csv'
#     df = pd.read_csv(csv_file_path)
#     print(df.head())
#     df = load_venues_csv(csv_file_path)
#     write_to_sqlite(df)
#     print("CSV data has been written to SQLite database.")
