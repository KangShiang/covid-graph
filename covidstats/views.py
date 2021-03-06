from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# Create your views here.
import json
import datetime
import requests
from dev_util import cache_util

def fetch_new_data_from_api():
    response = requests.get('https://corona.lmao.ninja/v2/historical')
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

def set_min_value(data, min_value):
    return list(filter(lambda x: x > min_value, data))

def country(request):
    data = get_data()
    countries = list(data["data"].keys())
    dictionary = {}
    for each in countries:
        pair = each.split("_")
        country_name = pair[0]
        province_name = each.split("_")[1] if len(each.split("_")) > 1 else None
        if country_name not in dictionary:
            dictionary[country_name] = {"province": [province_name]} if province_name is not None else {"province": None}
        else:
            if dictionary[country_name]["province"] is None and province_name is not None:
                dictionary[country_name]["province"] = [province_name]
            else:
                dictionary[country_name]["province"].append(province_name)

    keys = sorted(list(dictionary.keys()))
    response = list(map(lambda x: {
        "name": x,
        "province": sorted(dictionary[x]["province"]) if dictionary[x]["province"] is not None else None
    }, keys))
    return JsonResponse(response, safe=False)

def get(request):
    data = None
    country = request.GET.get("country")
    province = request.GET.get("province")
    sort = request.get("sort")
    min_count = 0 if request.GET.get("min") is None else int(request.GET.get("min"))

    data = get_data()
    max_count = 0
    locations = {}
    if province is not None:
        provinces = province.split('--')
        for entry in provinces:
            c = entry.split('-')[0]
            p = entry.split('-')[1]
            key = c + "_" + p if p is not None else c
            cp_data = get_none_zero_cases(data.get("data")[key])
            locations[p] = set_min_value(cp_data, min_count)
            if (len(locations[p]) > max_count): max_count = len(locations[p])

    if country is not None:
        countries = country.split('--')
        for c in countries:
            c_data = get_none_zero_cases(data.get("data")[c])
            locations[c] = set_min_value(c_data, min_count)
            if (len(locations[c]) > max_count): max_count = len(locations[c])


    response = format_response(locations, max_count)
    return JsonResponse(response, safe=False)


def timeseries(request):
    country = request.GET.get("country")
    province = request.GET.get("province")
    data = get_data()
    key = country
    if province is not None:
        key = key + "_" + province
    data = list(filter(lambda x: x["cases"] != 0, data.get("data")[key]))
    data = [ {"day": index, "cases": value["cases"]} for index, value in enumerate(data)]
    return JsonResponse(data, safe=False)


def format_response(locations, max_count):
    response = []
    day = 0
    while day < max_count:
        response.append([])
        if day == 0: response[0].append('Day')
        else: response[day].append(day)
        for location, data in locations.items():
            if day == 0: 
                response[0].append(location)
            elif day > len(data) - 1: 
                response[day].append(None)
            else: 
                response[day].append(data[day] if data[day] else None)
        day += 1

    return response


def demo(request):
    return HttpResponse(status=200)