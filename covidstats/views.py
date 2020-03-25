from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# Create your views here.
import json
import datetime
import requests
from dev_util import cache_util

def fetch_new_data_from_api():
    response = requests.get('https://corona.lmao.ninja/historical')
    data = response.json()
    cache_data = cache_util.process_api_data_for_cache(data)
    cache_util.store_cache(cache_data)
    return cache_data

def recover_from_file():
    try:
        with open("stats.json", "r") as file:
           return json.load(file)
    except:
        return None


def get_data():
    data = cache_util.get_cache()
    return data if data is not None else fetch_new_data_from_api()

def get_none_zero_cases(data):
    rslt = map(lambda x: x["cases"], data)
    return list(filter(lambda x: x != 0, rslt))

def get(request):
    data = None
    country = request.GET.get("country")
    province = request.GET.get("province")
    data = get_data()
    key = country + "_" + province if province is not None else country
    data = get_none_zero_cases(data.get("data")[key])
    return JsonResponse(data, safe=False)


def get2(request):
    data = None
    country = request.GET.get("country")
    province = request.GET.get("province")
    try:
        data = fetch_new_data_from_api()
    except:
        data=recover_from_file()

    locations = {}
    max_len = 0
    if province is not None:
        provinces = province.split(',')
        for entry in provinces:
            c = entry.split('-')[0]
            p = entry.split('-')[1]
            locations[p] = list(filter(lambda x: x != 0, get_province_total(data, c, p)))
            if (len(locations[p]) > max_len): max_len = len(locations[p])

    if country is not None:
        countries = country.split(',')
        for c in countries:
            locations[c] = list(filter(lambda x: x != 0, get_country_total(data, c)))
            if (len(locations[c]) > max_len): max_len = len(locations[c])
    
    response = format_response(locations, max_len)
    return JsonResponse(response, safe=False)


def format_response(locations, max_len):
    response = []
    day = 0
    while day < max_len:
        response.append([])
        if day == 0: response[0].append('Day')
        else: response[day].append(day)
        for location, data in locations.items():
            print(day)
            print(data)
            print('\n')
            if day == 0: 
                response[0].append(location)
            elif day > len(data) - 1: 
                response[day].append(None)
            else: 
                response[day].append(data[day] if data[day] else None)
        day += 1

    print(response)
    return response


def demo(request):
    data = None

    try:
        data = fetch_new_data_from_api()
    except:
        data = recover_from_file()

    canada = list(filter(lambda x: x != 0, get_country_total(data, "canada")))
    italy = list(filter(lambda x: x != 0, get_country_total(data, "italy")))
    china = list(filter(lambda x: x != 0, get_country_total(data, "china")))
    day = 0

    response = [[
            'Day',
            'Canada',
            'Italy',
            'China'
        ]
    ]

    while day < len(canada) or  day < len(canada) or  day < len(canada):
        c = canada[day] if day < len(canada) else None
        i = italy[day] if day < len(italy) else None
        ci = china[day] if day < len(china) else None
        response.append([day + 1, c, i, ci])
        day += 1

    return JsonResponse(response, safe=False)