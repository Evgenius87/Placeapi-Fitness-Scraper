import googlemaps
import time

from src.conf.config import settings




API_KEY = settings.google_maps_api_key

# def get_gym_info(city="Sidney", country="Australia"):
#     gmaps = googlemaps.Client(key=API_KEY)

#     location = f"{city}, {country}"
#     geocode_result = gmaps.geocode(location)
#     lat = geocode_result[0]['geometry']['location']['lat']
#     lng = geocode_result[0]['geometry']['location']['lng']

#     all_results = []


#     gyms = gmaps.places_nearby(
#         location=(lat, lng),
#         radius=7000,
#         type="gym"
#     )

#     fitness = gmaps.places_nearby(
#         location=(lat, lng),
#         radius=7000,
#         keyword="fitness"
#     )

#     all_results = gyms["results"] + fitness["results"]

#     all_results.extend(places_result["results"])

#     while "next_page_token" in places_result:
#         time.sleep(2)
#         places_result = gmaps.places_nearby(
#             location=(lat, lng),
#             radius=5000,
#             type="gym",
#             page_token=places_result["next_page_token"]
#         )
#         all_results.extend(places_result["results"])

#     formatted_data = []
#     for place in all_results:
#         formatted_data.append({
#             "Name": place.get("name"),
#             "Address": place.get("vicinity"),
#             "Rating": place.get("rating", "Немає рейтингу"),
#             "Latitude": place["geometry"]["location"]["lat"],
#             "Longitude": place["geometry"]["location"]["lng"],
#         })
#     return formatted_data

def get_gym_info(city="Sidney", country="Australia"):
    gmaps = googlemaps.Client(key=API_KEY)

    location = f"{city}, {country}"
    geocode_result = gmaps.geocode(location)
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']

    def get_all_results(search_params):
        all_results = []
        
        response = gmaps.places_nearby(**search_params)
        all_results.extend(response.get("results", []))

        
        while "next_page_token" in response:
            time.sleep(2)  
            
            try:
                response = gmaps.places_nearby(
                    location=search_params["location"],
                    radius=search_params["radius"],
                    type=search_params.get("type"),
                    keyword=search_params.get("keyword"),
                    page_token=response["next_page_token"]
                )
                new_results = response.get("results", [])
                all_results.extend(new_results)
                
            except Exception as e:
                break
        
        return all_results

    gym_params = {
        "location": (lat, lng),
        "radius": 7000,
        "type": "gym"
    }
    gym_results = get_all_results(gym_params)

    fitness_params = {
        "location": (lat, lng),
        "radius": 7000,
        "keyword": "fitness"
    }
    fitness_results = get_all_results(fitness_params)

    all_places = gym_results + fitness_results
    seen_place_ids = set()
    unique_results = []
    
    for place in all_places:
        place_id = place.get("place_id")
        if place_id and place_id not in seen_place_ids:
            seen_place_ids.add(place_id)
            unique_results.append(place)

    formatted_data = []
    for place in unique_results:
        formatted_data.append({
            "Name": place.get("name"),
            "Address": place.get("vicinity"),
            "Rating": place.get("rating", "Немає рейтингу"),
            "Latitude": place["geometry"]["location"]["lat"],
            "Longitude": place["geometry"]["location"]["lng"],
        })
    
    return formatted_data