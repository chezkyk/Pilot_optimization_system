import requests
import math
import json
from aircraft import Aircraft
from pilot import Pilot


list_of_aircraft = []
list_of_pilots = []
my_key = "d81e4e34922bb40ff35eda1df0dd91ae"
Beer_Sheba_cordinates = None # neer Nevatim, Camp

def get_coordinates(city_name,api_key):
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}")
    json_data = response.json()
    lat = json_data[0]['lat']
    lon = json_data[0]['lon']

    print(f"Latitude: {lat}, Longitude: {lon}")

get_coordinates("teheran", my_key)
def get_aircraft_data_from_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data:
        aircraft_obj = Aircraft(
            type=item['type'],
            speed=item['speed'],
            fuel_capacity=item['fuel_capacity'],
        )
        list_of_aircraft.append(aircraft_obj)

    return list_of_aircraft

# path = "C:\\Users\\Admin\\PycharmProjects\\Pilot_optimization_system\\aircrafts.json"
# aircraft_array = get_aircraft_data_from_json(path)
# for aircraft in aircraft_array:
#     print(aircraft.type, aircraft.speed, aircraft.fuel_capacity)

def get_pilot_data_from_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data:
        pilot_obj = Pilot(
            name=item['name'],
            skill_level=item['skill_level']
        )
        list_of_pilots.append(pilot_obj)
    return list_of_pilots


# path = "C:\\Users\\Admin\\PycharmProjects\\Pilot_optimization_system\\pilots.json"
# pilot_array = get_pilot_data_from_json(path)
# for pilot in pilot_array:
#     print(pilot.name, pilot.skill_level)


















weights = {
    "distance": 0.15,
    "aircraft_type": 0.20,
    "pilot_skill": 0.20,
    "weather_conditions": 0.20,
    "execution_time": 0.10,
    "priority": 0.15
}


def weather_score(weather):
    if weather["condition"] == "Clear":
        return 1.0
    elif weather["condition"] == "Clouds":
        return 0.7
    elif weather["condition"] == "Rain":
        return 0.4
    elif weather["condition"] == "Stormy":
        return 0.2
    else:
        return 0


# Function to calculate the distance between two coordinates using the Haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371.0  # Radius of the Earth in kilometers
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    # Calculate differences between the coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    # Apply Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Calculate the distance
    distance = r * c
    return distance
