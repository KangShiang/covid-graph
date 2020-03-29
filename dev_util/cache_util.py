import json
import datetime

def get_cache():
    try:
        with open("cache.json", "r") as cache_file:
            data = json.load(cache_file)
            date = data.get("date")
            today = datetime.datetime.now() + datetime.timedelta(days=1)
            date_str = today.strftime("%-m/%-d/20")
            return data if date_str == date else None
    except FileNotFoundError as e:
        print(e)
        return None

def store_cache(data):
    with open("cache.json", "w") as cache_file:
        cache_file.write(json.dumps(data))

def process_place_data(place):
    day = 0
    start_date = datetime.datetime(2020, 1, 22, 0, 0, 0)
    date = start_date + datetime.timedelta(days=day)
    cases = place.get("timeline").get("cases")
    date_str = date.strftime("%-m/%-d/20")
    result = []
    while cases.get(date_str) is not None:
        result.append({
            "date": date_str,
            "cases": 0 if cases.get(date_str) == "" else int(cases.get(date_str))
        })
        day += 1
        date = start_date + datetime.timedelta(days=day)
        date_str = date.strftime("%-m/%-d/20")
    return result

def add_province_to_country(cached_country_data, province_data):
    day = 0
    start_date = datetime.datetime(2020, 1, 22, 0, 0, 0)
    date = start_date + datetime.timedelta(days=day)
    cases = province_data.get("timeline").get("cases")
    date_str = date.strftime("%-m/%-d/20")
    while cases.get(date_str) is not None:
        case = 0 if cases.get(date_str) == "" else int(cases.get(date_str))
        cached_country_data[day]["cases"] += case
        day += 1
        date = start_date + datetime.timedelta(days=day)
        date_str = date.strftime("%-m/%-d/20")
    return cached_country_data

def process_api_data_for_cache(data):
    today = datetime.datetime.now() + datetime.timedelta(days=1)
    date_str = today.strftime("%-m/%-d/20")
    cache = {}
    cache["date"] = date_str
    cache["data"] = {}
    for place in data:
        country = place.get("country")
        province = place.get("province")
        if cache.get("data").get(country) is None:
            cache["data"][country] = process_place_data(place)
            if province is not None:
                cache["data"][country + "_" + province] = process_place_data(place)
        else:
            country_data = cache.get("data").get(country)
            country_data = add_province_to_country(country_data, place)
            cache["data"][country] = country_data
            if province is not None:
                cache["data"][country+ "_" + province] = process_place_data(place)
    return cache
