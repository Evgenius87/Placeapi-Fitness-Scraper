import aiohttp
import asyncio

from src.conf.config import settings

OVERPASS_URL = settings.overpass_url
NOMINATIM_URL = settings.nominatim_url


async def _query_overpass(query: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(OVERPASS_URL, params={"data": query}) as resp:
            if resp.status != 200:
                raise Exception(f"Overpass API error: {resp.status}")
            return await resp.json()


async def _get_city_coordinates(city: str, country: str):
    params = {
        "q": f"{city}, {country}",
        "format": "json",
        "limit": 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(NOMINATIM_URL, params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Nominatim API error: {resp.status}")
            data = await resp.json()
            if not data:
                return None
            return float(data[0]["lat"]), float(data[0]["lon"])


async def _search_by_area(city: str):
    query = f"""
    [out:json][timeout:180];
    area["name"="{city}"]["boundary"="administrative"]->.cityArea;
    (
      // --- 1. Основні теги ---
      nwr(area.cityArea)["amenity"~"^(gym|dojo|studio|training|health_club|community_centre)$"];
      nwr(area.cityArea)["leisure"~"^(fitness_centre|fitness_station|sports_centre|dance|climbing|wellness|club|health_club)$"];
      nwr(area.cityArea)["sport"~"^(fitness|yoga|pilates|boxing|martial_arts|kickboxing|aikido|karate|judo|taekwondo|kung_fu|crossfit|climbing|bouldering|parkour|dance|cheerleading|aerobics|cycling|spinning|running|personal_training|strength_training|stretching)$"];
      nwr(area.cityArea)["club"~"^(sport|fitness|gym)$"];
      nwr(area.cityArea)["shop"~"^(sports|fitness_equipment)$"];

      // --- 2. Будівлі ---
      nwr(area.cityArea)["building"~"^(fitness_centre|gym|sports_hall|dojo)$"];

      // --- 3. Назви (fallback) ---
      nwr(area.cityArea)["name"~"(gym|fitness|yoga|pilates|boxing|dance|crossfit|dojo)", i];
    );
    out center;
    """
    return await _query_overpass(query)


async def _search_by_coordinates(lat: float, lon: float, radius: int = 50000):
    query = f"""
    [out:json][timeout:180];
    (
      // --- 1. Основні теги ---
      nwr(around:{radius},{lat},{lon})["amenity"~"^(gym|dojo|studio|training|health_club|community_centre)$"];
      nwr(around:{radius},{lat},{lon})["leisure"~"^(fitness_centre|fitness_station|sports_centre|dance|climbing|wellness|club|health_club)$"];
      nwr(around:{radius},{lat},{lon})["sport"~"^(fitness|yoga|pilates|boxing|martial_arts|kickboxing|aikido|karate|judo|taekwondo|kung_fu|crossfit|climbing|bouldering|parkour|dance|cheerleading|aerobics|cycling|spinning|running|personal_training|strength_training|stretching)$"];
      nwr(around:{radius},{lat},{lon})["club"~"^(sport|fitness|gym)$"];
      nwr(around:{radius},{lat},{lon})["shop"~"^(sports|fitness_equipment)$"];

      // --- 2. Будівлі ---
      nwr(around:{radius},{lat},{lon})["building"~"^(fitness_centre|gym|sports_hall|dojo)$"];

      // --- 3. Назви (fallback) ---
      nwr(around:{radius},{lat},{lon})["name"~"(gym|fitness|yoga|pilates|boxing|dance|crossfit|dojo)", i];
    );
    out center;
    """
    return await _query_overpass(query)


async def get_gym_info(city: str, country: str):
    data = await _search_by_area(city)

    if not data.get("elements"):
        coords = await _get_city_coordinates(city, country)
        if coords:
            data = await _search_by_coordinates(*coords)
        else:
            return []

    places = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = (
            tags.get("name")
            or tags.get("name:en")
            or tags.get("name:uk")
            or "Unnamed"
        )
        category = (
            tags.get("amenity")
            or tags.get("leisure")
            or tags.get("sport")
            or tags.get("club")
            or tags.get("shop")
            or tags.get("building")
            or "Unknown"
        )
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")

        places.append({
            "Name": name,
            "Category": category,
            "Longitude": lon,
            "Latitude": lat,
        })

    print(f"✅ Found {len(places)} fitness places in {city}, {country}")
    return places

##########################################################3
# import aiohttp
# import asyncio

# from src.conf.config import settings

# OVERPASS_URL = settings.overpass_url
# NOMINATIM_URL = settings.nominatim_url

# SPORTS_CLUBS = {"football", "soccer", "rugby", "tennis", "cricket", "hockey"}


# async def _query_overpass(query: str):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(OVERPASS_URL, params={"data": query}) as resp:
#             if resp.status != 200:
#                 raise Exception(f"Overpass API error: {resp.status}")
#             return await resp.json()


# async def _get_city_coordinates(city: str, country: str):
#     params = {
#         "q": f"{city}, {country}",
#         "format": "json",
#         "limit": 1
#     }
#     async with aiohttp.ClientSession() as session:
#         async with session.get(NOMINATIM_URL, params=params) as resp:
#             if resp.status != 200:
#                 raise Exception(f"Nominatim API error: {resp.status}")
#             data = await resp.json()
#             if not data:
#                 return None
#             return float(data[0]["lat"]), float(data[0]["lon"])


# def _build_overpass_query(city: str = None, lat: float = None, lon: float = None, radius: int = 50000):
#     if city:
#         area_clause = f'area["name"="{city}"]["boundary"="administrative"]->.searchArea;'
#         location = "area.searchArea"
#     else:
#         area_clause = ""
#         location = f"around:{radius},{lat},{lon}"

#     query = f"""
#     [out:json][timeout:180];
#     {area_clause}
#     (
#       // --- Core fitness and gyms ---
#       nwr({location})["amenity"~"^(gym|dojo|studio|training|health_club)$"];
#       nwr({location})["leisure"~"^(fitness_centre|fitness_station|dance|climbing|wellness)$"];

#       // --- Sports that are usually boutique studios ---
#       nwr({location})["sport"~"^(fitness|yoga|pilates|boxing|martial_arts|kickboxing|aikido|karate|judo|taekwondo|kung_fu|crossfit|bouldering|parkour|dance|aerobics|personal_training|strength_training|stretching)$"];

#       // --- Names fallback ---
#       nwr({location})["name"~"(gym|fitness|yoga|pilates|boxing|dance|crossfit|dojo|studio)", i];
#     );
#     out center;
#     """
#     return query


# async def _search_by_area(city: str):
#     query = _build_overpass_query(city=city)
#     return await _query_overpass(query)


# async def _search_by_coordinates(lat: float, lon: float, radius: int = 50000):
#     query = _build_overpass_query(lat=lat, lon=lon, radius=radius)
#     return await _query_overpass(query)


# async def get_gym_info(city: str, country: str, exclude_sports: bool = True):
#     data = await _search_by_area(city)

#     if not data.get("elements"):
#         coords = await _get_city_coordinates(city, country)
#         if coords:
#             data = await _search_by_coordinates(*coords)
#         else:
#             return []

#     places = []
#     for element in data.get("elements", []):
#         tags = element.get("tags", {})
#         name = (
#             tags.get("name")
#             or tags.get("name:en")
#             or tags.get("name:uk")
#             or "Unnamed"
#         )
#         category = (
#             tags.get("amenity")
#             or tags.get("leisure")
#             or tags.get("sport")
#             or tags.get("club")
#             or tags.get("shop")
#             or tags.get("building")
#             or "Unknown"
#         )
#         lat = element.get("lat") or element.get("center", {}).get("lat")
#         lon = element.get("lon") or element.get("center", {}).get("lon")

#         # Skip big sports clubs if needed
#         if exclude_sports and category in SPORTS_CLUBS:
#             continue

#         places.append({
#             "Name": name,
#             "Category": category,
#             "Longitude": lon,
#             "Latitude": lat,
#         })

#     print(f"✅ Found {len(places)} fitness places in {city}, {country}")
#     return places
