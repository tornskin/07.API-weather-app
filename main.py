import json
import requests
from geopy.geocoders import Nominatim
from datetime import datetime

API_URL = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}" \
          "&hourly=rain&daily=rain_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}"


class WeatherForecast:
    def __init__(self):
        self.data = self.read_data_from_file()

    def retrieve_data_from_api(self, latitude, longitude, searched_date):
        response = requests.get(API_URL.format(latitude=latitude, longitude=longitude, searched_date=searched_date))
        data = response.json()
        return data

    def find_coordinates_for_city(self, city):
        geolocator = Nominatim(user_agent="MyApp")
        location = geolocator.geocode(city)

        return (location.latitude, location.longitude) if location else (None, None)

    def check_raining_sum(self, data):
        raining_sum = data.get("daily", {}).get("rain_sum", [0.0])[0]
        if raining_sum > 0.0:
            return "Bedzie padać"
        elif raining_sum == 0.0:
            return "Nie będzie padać"
        else:
            return "Nie wiem"

    def read_data_from_file(self):
        try:
            with open("opady.txt") as file:
                data_in_file = file.read()
                return json.loads(data_in_file) if data_in_file else {}
        except FileNotFoundError:
            return {}

    def write_data_to_file(self):
        with open("opady.txt", mode="w") as file:
            file.write(json.dumps(self.data))

    def retrieve_data(self, city, date):
        city_data = self.data.get(city, {})
        raining_data = city_data.get(date)
        if raining_data is not None:
            return raining_data

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Nieprawidłowy format daty.")
            return None

        latitude, longitude = self.find_coordinates_for_city(city)
        if latitude is None or longitude is None:
            print("Nieprawidłowa nazwa miasta.")
            return None

        data = self.retrieve_data_from_api(latitude, longitude, date)
        raining_data = self.check_raining_sum(data)
        city_data[date] = raining_data
        self.data[city] = city_data
        self.write_data_to_file()
        return raining_data

    def __setitem__(self, key, value):
        city, date = key
        city_data = self.data.get(city, {})
        city_data[date] = value
        self.data[city] = city_data
        self.write_data_to_file()

    def __getitem__(self, key):
        city, date = key
        return self.retrieve_data(city, date)

    def __iter__(self):
        for city, city_data in self.data.items():
            for date in city_data.keys():
                yield city, date

    def items(self):
        return ((city, date, self.data[city][date]) for city in self.data for date in self.data[city])


if __name__ == "__main__":
    weather_forecast = WeatherForecast()

    city = input("Podaj miasto, dla którego chcesz sprawdzić pogodę: ")
    date = input("Podaj datę, dla której chcesz sprawdzić pogodę (w formacie YYYY-mm-dd): ")

    raining_data = weather_forecast[city, date]
    if raining_data is not None:
        print(raining_data)
