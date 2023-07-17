import json
import requests
from geopy.geocoders import Nominatim
from datetime import datetime

API_URL = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}" \
          "&hourly=rain&daily=rain_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}"


def retrieve_data_from_api(latitude, longitude, searched_date):
    response = requests.get(API_URL.format(latitude=latitude, longitude=longitude, searched_date=searched_date))
    data = response.json()
    return data


def find_coordinates_for_city(city):
    geolocator = Nominatim(user_agent="MyApp")
    location = geolocator.geocode(city)

    return (location.latitude, location.longitude) if location else (None, None)


def check_raining_sum(data):
    raining_sum = data.get("daily", {}).get("rain_sum", [0.0])[0]
    if raining_sum > 0.0:
        return "Bedzie padać"
    elif raining_sum == 0.0:
        return "Nie będzie padać"
    else:
        return "Nie wiem"


def read_data_from_file():
    try:
        with open("opady.txt") as file:
            data_in_file = file.read()
            return json.loads(data_in_file) if data_in_file else {}
    except FileNotFoundError:
        return {}


def write_data_to_file(data):
    with open("opady.txt", mode="w") as file:
        file.write(json.dumps(data))


def retrieve_data(file_data, city, date):
    city_data = file_data.get(city, {})
    raining_data = city_data.get(date)
    if raining_data is not None:
        return raining_data, False

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Nieprawidłowy format daty.")
        return None, False

    latitude, longitude = find_coordinates_for_city(city)
    if latitude is None or longitude is None:
        print("Nie można odnaleźć współrzędnych dla podanego miasta.")
        return None, False

    data = retrieve_data_from_api(latitude, longitude, date)
    raining_data = check_raining_sum(data)
    city_data[date] = raining_data
    return raining_data, True


city = input("Podaj miasto, dla którego chcesz sprawdzić pogodę: ")
date = input("Podaj datę, dla której chcesz sprawdzić pogodę (w formacie YYYY-mm-dd): ")

data = read_data_from_file()
raining_data, write_new_data_to_file = retrieve_data(data, city, date)
if write_new_data_to_file:
    write_data_to_file(data)
if raining_data is not None:
    print(raining_data)
