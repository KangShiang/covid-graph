from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# Create your views here.
import json
import datetime
import requests


def get_latest_data():
    response = requests.get('https://corona.lmao.ninja/historical')
    data = response.json()
    return data

def recover_from_file():
    try:
        with open("stats.json", "r") as file:
           return json.load(file)
    except:
        return None

def get_country_total(data, country):
    start_date = datetime.datetime(2020, 1, 22, 0, 0, 0)
    result = []
    for place in data:
        day = 0
        if country == place.get("country"):
            timeline = place.get("timeline").get("cases")
            date = start_date + datetime.timedelta(days=day)
            date_str = date.strftime("%-m/%-d/20")
            while timeline.get(date_str) is not None:
                if len(result) > day:
                    result[day] = result[day] + int(timeline.get(date_str))
                else:
                    result.append(int(timeline.get(date_str)))
                day += 1
                date = start_date + datetime.timedelta(days=day)
                date_str = date.strftime("%-m/%-d/20")
    return result


def get_province_total(data, country, province):
    start_date = datetime.datetime(2020, 1, 22, 0, 0, 0)
    result = []
    for place in data:
        day = 0
        if country == place.get("country") and province == place.get("province"):
            timeline = place.get("timeline").get("cases")
            date = start_date + datetime.timedelta(days=day)
            date_str = date.strftime("%-m/%-d/20")
            while timeline.get(date_str) is not None:
                result.append(int(timeline.get(date_str)))
                day += 1
                date = start_date + datetime.timedelta(days=day)
                date_str = date.strftime("%-m/%-d/20")
    return result

def get(request):
    data = None
    country = request.GET.get("country")
    province = request.GET.get("province")
    try:
        data = get_latest_data()
    except:
        data = recover_from_file()

    response = None
    if province is not None:
        response = get_province_total(data, country, province)
    else:
        response = get_country_total(data, country)

    return JsonResponse(response, safe=False)


def get2(request):
    data = None
    country = request.GET.get("country")
    province = request.GET.get("province")
    min_count = request.GET.get("min")
    try:
        data = get_latest_data()
    except:
        data=recover_from_file()

    locations = {}
    max_count = 0
    if province is not None:
        provinces = province.split('--')
        for entry in provinces:
            c = entry.split('-')[0]
            p = entry.split('-')[1]
            locations[p] = list(filter(lambda x: x != 0, get_province_total(data, c, p)))
            if (len(locations[p]) > max_count): max_count = len(locations[p])

    if country is not None:
        countries = country.split('--')
        for c in countries:
            locations[c] = list(filter(lambda x: x != 0, get_country_total(data, c)))
            if (len(locations[c]) > max_count): max_count = len(locations[c])
    
    response = format_response(locations, max_count)
    return JsonResponse(response, safe=False)


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
    data = None
    try:
        data = get_latest_data()
    except:
        data = recover_from_file()

    canada = list(filter(lambda x: x != 0, get_country_total(data, "canada")))
    usa = list(filter(lambda x: x != 0, get_country_total(data, "usa")))
    italy = list(filter(lambda x: x != 0, get_country_total(data, "italy")))
    china = list(filter(lambda x: x != 0, get_country_total(data, "china")))

    day = 0

    response = [[
            'Day',
            'Canada',
            'US',
            'Italy',
            'China'
        ]
    ]

    while day < len(canada) or  day < len(canada) or  day < len(canada):
        c = canada[day] if day < len(canada) else None
        u = usa[day] if day < len(usa) else None
        i = italy[day] if day < len(italy) else None
        ci = china[day] if day < len(china) else None
        response.append([day + 1, c, u, i, ci])
        day += 1

    return JsonResponse(response, safe=False)