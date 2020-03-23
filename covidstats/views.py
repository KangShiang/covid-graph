from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# Create your views here.
import json
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

def process_data(data, country, provience):
    for place in data:
        if country == place.get("country") and provience == place.get("provience"):
            return place
    return None

def get(request):
    data = None
    country = request.GET.get("country")
    province = request.GET.get("province")
    try:
        data = get_latest_data()
    except:
        data = recover_from_file()

    response = process_data(data, country, province)

    return JsonResponse(response, safe=False)