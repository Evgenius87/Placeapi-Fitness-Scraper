def slpit_message(message: str) -> tuple:
    try:
        split_message = message.split(",")
        city = split_message[0].strip()
        country = split_message[1].strip()
        print(f"City: {city}, Country: {country}")
        return city, country
    except IndexError:
        return None, None