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
    [out:json][timeout:60];
    area["name"="{city}"]["boundary"="administrative"]->.cityArea;
    (
      nwr(area.cityArea)["amenity"="gym"];
      nwr(area.cityArea)["amenity"="dojo"];
      nwr(area.cityArea)["amenity"="health_club"];

      nwr(area.cityArea)["leisure"~"^(fitness_centre|sports_centre)$"];

      nwr(area.cityArea)["sport"~"^(yoga|boxing|martial_arts)$"];
    );
    out center;
    """
    return await _query_overpass(query)


async def _search_by_coordinates(lat: float, lon: float, radius: int = 50000):
    query = f"""
    [out:json][timeout:60];
    (
      nwr(around:{radius},{lat},{lon})["amenity"="gym"];
      nwr(around:{radius},{lat},{lon})["amenity"="dojo"];
      nwr(around:{radius},{lat},{lon})["amenity"="health_club"];

      nwr(around:{radius},{lat},{lon})["leisure"~"^(fitness_centre|sports_centre)$"];

      nwr(around:{radius},{lat},{lon})["sport"~"^(yoga|boxing|martial_arts)$"];
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

