import requests
import os
from pathlib import Path
import pandas as pd
from utils.data_loader import read_from_sqlite, write_to_sqlite

def search_place(place: str, api_key):

    FIELDS = ["name,geometry","formatted_address","business_status", "place_id"]
    ENDPOINT = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": place,
        "inputtype": "textquery",
        "fields": ",".join(FIELDS),
        "key": api_key
    }
    response = requests.get(ENDPOINT, params=params)

    if response.status_code != 200:
        print("Error:", response.text)
        return None
    data = response.json()
    
    if not data.get("candidates"):
        return None

    candidate = data["candidates"][0]
    result = {
        "name": candidate.get("name"),
        "address": candidate.get("formatted_address"),
        "lat": candidate["geometry"]["location"]["lat"],
        "lng": candidate["geometry"]["location"]["lng"],
        "place_id": candidate["place_id"]
    }

    return result

def get_details(place_id, api_key):
    DETAIL_ENDPOINT = "https://maps.googleapis.com/maps/api/place/details/json"
    DETAIL_FIELDS = ["formatted_phone_number", 
                "website",
                #"opening_hours",
                #"editorial_summary",
                "international_phone_number",
                "photos",
                "price_level",
                "rating",
                #"serves_vegetarian_food",
                #"serves_wine",
                #"serves_dinner",
                #"wheelchair_accessible_entrance",
                "reviews"
                ]
    params = {
        "place_id": place_id,
        "fields": ",".join(DETAIL_FIELDS),
        "key": api_key
    }
    response = requests.get(DETAIL_ENDPOINT, params=params)

    if response.status_code != 200:
        print("Error:", response.text)
        return None
    data = response.json()

    result_data = data.get('result', {})
    phone_number = result_data.get('international_phone_number')
    website = result_data.get('website')
    price_level = result_data.get('price_level')
    rating = result_data.get('rating')
    photo_references = [photo['photo_reference'] for photo in result_data.get('photos', [])]
    reviews = [review['text'] for review in result_data.get('reviews', [])]

    result = {
        "place_id": place_id,
        "phone_number": phone_number,
        "website": website,
        "price_level": price_level,
        "rating": rating,
        "photo_references": photo_references,
        "reviews": reviews
    }

    return result

def get_place_photo(photo_reference, api_key, max_width=2400):
    endpoint = "https://maps.googleapis.com/maps/api/place/photo"
    params = {
        "photo_reference": photo_reference,
        "maxwidth": max_width,
        "key": api_key
    }
    response = requests.get(endpoint, params=params)
    print("Status code:", response.status_code)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code}", response.text)
        return None
    
def save_photo_to_dir(output_path, photo_data):
    if photo_data:
        with open(output_path, "wb") as f:
            f.write(photo_data)
        print(f"Photo saved to {output_path}")
    else:
        print("No photo data to save.")

def write_photos(photo_references: list, api_key: str, folder_name: str):
    for idx, photo_reference in enumerate(photo_references):
        photo_data = get_place_photo(photo_reference=photo_reference, api_key=api_key)

        # Create the data folder
        folder_path = Path(os.path.join(os.curdir, folder_name))
        folder_path.mkdir(parents=True, exist_ok=True)

        # Write all photos to folder
        save_photo_to_dir(os.path.join(folder_name, f"{idx}.jpeg"), photo_data)

# def enrich_venues_from_google():
#     """
#     Enriches venue data with information from the Google Places API.
#     """
#     # 1. Read the API key from an environment variable
#     api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
#     if not api_key:
#         print("Error: GOOGLE_PLACES_API_KEY environment variable not set.")
#         print("Please set the GOOGLE_PLACES_API_KEY environment variable with your Google Places API key.")
#         return
#
#     # 2. Load the venues from the database
#     df = read_from_sqlite()
#
#     # 3. Iterate through each venue
#     enriched_data = []
#     for index, row in df.iterrows():
#         print(f"Enriching {row['Name']}...")
#         # 4. Search for the venue using the Google Places API
#         place_info = search_place(f"{row['Name']}, {row['Address']}", api_key)
#         if not place_info:
#             print(f"Could not find {row['Name']} on Google Maps.")
#             continue
#
#         # 5. Get the venue details
#         details = get_details(place_info["place_id"], api_key)
#         if not details:
#             print(f"Could not get details for {row['Name']}.")
#             continue
#
#         # 6. Download the venue photos
#         if details["photo_references"]:
#             write_photos(details["photo_references"], api_key, f"data/output/photos/{row['Name'].replace(' ', '_')}")
#
#         # 7. Update the DataFrame
#         enriched_data.append({
#             **row.to_dict(),
#             **place_info,
#             **details
#         })
#
#     # 8. Save the enriched data
#     enriched_df = pd.DataFrame(enriched_data)
#     write_to_sqlite(enriched_df, table_name="enriched_venues_google")
#     enriched_df.to_csv("data/output/enriched_venues_google.csv", index=False)
#     print("Enriched data saved to data/output/enriched_venues_google.csv and enriched_venues_google table.")

#if __name__ == '__main__':
#    enrich_venues_from_google()