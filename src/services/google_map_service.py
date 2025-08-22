import asyncio
import googlemaps
import time
from src.conf.config import settings


API_KEY = settings.google_maps_api_key
gmaps = googlemaps.Client(key=API_KEY)


def get_all_results_sync(search_params):
    all_results = []
    response = gmaps.places_nearby(**search_params)
    all_results.extend(response.get("results", []))

    while "next_page_token" in response:
        time.sleep(2)  
        response = gmaps.places_nearby(
            location=search_params["location"],
            radius=search_params["radius"],
            type=search_params.get("type"),
            keyword=search_params.get("keyword"),
            page_token=response["next_page_token"]
        )
        all_results.extend(response.get("results", []))
    return all_results


async def get_all_results(params):
    return await asyncio.to_thread(get_all_results_sync, params)


def get_city_bounds(city, country):
    location = f"{city}, {country}"
    geocode_result = gmaps.geocode(location)
    bounds = geocode_result[0]["geometry"]["bounds"]
    ne = bounds["northeast"]
    sw = bounds["southwest"]
    return (ne, sw)


def generate_grid(ne, sw, step_km=2.0):
    lat_step = step_km / 111.0
    lng_step = step_km / 85.0
    lat = sw["lat"]
    points = []
    while lat <= ne["lat"]:
        lng = sw["lng"]
        while lng <= ne["lng"]:
            points.append((lat, lng))
            lng += lng_step
        lat += lat_step
    return points


SEARCH_KEYWORDS = ["gym", "fitness", "yoga", "boxing", "martial arts", "sports complex"]


async def fetch_point_data(point, radius, keywords=None):
    results = []
    if keywords is None:
        keywords = ["gym", "fitness"]

    for keyword in keywords:
        params = {"location": point, "radius": radius}
        if keyword == "gym":
            params["type"] = "gym"
        else:
            params["keyword"] = keyword

        res = await get_all_results(params)
        results.extend(res)

    return results


async def get_gym_info(city="New York", country="USA"):
    ne, sw = get_city_bounds(city, country)
    lat_span = ne["lat"] - sw["lat"]
    lng_span = ne["lng"] - sw["lng"]

    if lat_span > 0.2 or lng_span > 0.2:  
        radius = 3000
        step_km = 2.0
        limit_points = 500
        keywords = SEARCH_KEYWORDS

    else:  
        radius = 3000
        step_km = 2.5
        limit_points = 200
        keywords = ["gym", "fitness"]


    points = generate_grid(ne, sw, step_km=step_km)
    print(f"🔎 Generated {len(points)} points (limit {limit_points})")

    tasks = []
    for i, point in enumerate(points[:limit_points]):
        tasks.append(fetch_point_data(point, radius, keywords))

    results = await asyncio.gather(*tasks)

    all_places = []
    seen_place_ids = set()

    for res in results:
        for place in res:
            place_id = place.get("place_id")
            if place_id and place_id not in seen_place_ids:
                seen_place_ids.add(place_id)
                all_places.append({
                    "Name": place.get("name"),
                    "Address": place.get("vicinity"),
                    "Rating": place.get("rating", "no rating"),
                    "Latitude": place["geometry"]["location"]["lat"],
                    "Longitude": place["geometry"]["location"]["lng"],
                })
    return all_places
