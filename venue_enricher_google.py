import requests


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

    phone_number = data['result']['international_phone_number']
    phone_number = data['result']['website']
    price_level = data['result']['price_level']
    rating = data['result']['rating']
    photo_references = [photo['photo_reference'] for photo in data['result']['photos']]
    reviews = [review['text'] for review in data['result']['reviews']]

    result = {
        "place_id": place_id,
        "phone_number": phone_number,
        "price_level": price_level,
        "rating": rating,
        "photo_references": photo_references,
        "reviews": reviews
    }

    return result