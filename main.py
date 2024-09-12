import os

import requests
import math
import json
from aircraft import Aircraft
from pilot import Pilot
from mission import Mission
import csv


list_of_aircraft = []
list_of_pilots = []
dict_of_target = {}
dict_of_weather = {}
my_key = "d81e4e34922bb40ff35eda1df0dd91ae"
Beer_Sheba_cordinates = (31.2457442,34.7925181) # neer Nevatim, Camp
#***********************************************************************************************************************
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

#***********************************************************************************************************************

def get_coordinates(city_name):
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={my_key}")
    json_data = response.json()
    lat = json_data[0]['lat']
    lon = json_data[0]['lon']

    return lat, lon

def return_json_data_targets(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for target in data:
            dict_of_target[target['City']] = target

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

def calculate_distance(city_info):
    city_name = city_info['City']
    coordinates = get_coordinates(city_name)
    if coordinates:
        distance = haversine_distance(Beer_Sheba_cordinates[0], Beer_Sheba_cordinates[1], coordinates[0], coordinates[1])
        city_info['Distance'] = int(distance)

def update_distances():
    for target in dict_of_target.values():
        calculate_distance(target)
def save_updated_data_to_file(path_file):
    with open(path_file, 'w', encoding='utf-8') as file:
        json.dump(list(dict_of_target.values()), file, indent=4)
return_json_data_targets("C:\\Users\\Admin\\PycharmProjects\\Pilot_optimization_system\\air_strike_targets.json")
update_distances()
save_updated_data_to_file("C:\\Users\\Admin\\PycharmProjects\\Pilot_optimization_system\\air_strike_targets_updated.json")

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

path = "C:\\Users\\Admin\\PycharmProjects\\Pilot_optimization_system\\aircrafts.json"
aircraft_array = get_aircraft_data_from_json(path)
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


path = "C:\\Users\\Admin\\PycharmProjects\\Pilot_optimization_system\\pilots.json"
pilot_array = get_pilot_data_from_json(path)
# for pilot in pilot_array:
#     print(pilot.name, pilot.skill_level)
def extract_weather_data(json_data, target_date, city_name):
        data = json.loads(json_data)
        for item in data['list']:
            if item['dt_txt'] == target_date:
                weather_main = item['weather'][0]['main']
                wind_speed = item['wind']['speed']
                cloud_coverage = item['clouds']['all']
                return {
                    city_name: {
                        'weather_main': weather_main,
                        'wind_speed': wind_speed,
                        'cloud_coverage': cloud_coverage
                    }
                }
        return None

def get_weather(city):
    for i in range(15):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={my_key}"
        response = requests.get(url)
        data = extract_weather_data(response.text, "2024-09-13 00:00:00", city)
        if data:
            dict_of_weather.update(data)
            return
def start_weather():
    city_names = list(dict_of_target.keys())
    for city in city_names:
        get_weather(city)
start_weather()


def calculate_execution_time(distance, speed):
    return distance / speed


# This function returns the max distance and speed given by the files.
def get_max_values(missions):
    max_distance = max(mission.distance for mission in missions)
    max_speed = max(mission.aircraft_speed for mission in missions)
    return max_distance, max_speed


def calculate_mission_score(mission, weights, max_distance, max_speed):
    distance_score = mission.distance / max_distance
    aircraft_score = mission.aircraft_speed / max_speed
    pilot_score = mission.pilot_skill / 10
    weather_score_value = weather_score({"condition": mission.weather_conditions})
    execution_time = calculate_execution_time(mission.distance, mission.aircraft_speed)
    execution_time_score = 1 - (execution_time / 24) # the lowest execution time will be the highest score
    priority_score = mission.priority / 5
    total_score = (
            weights["distance"] * distance_score +
            weights["aircraft_type"] * aircraft_score +
            weights["pilot_skill"] * pilot_score +
            weights["weather_conditions"] * weather_score_value +
            weights["execution_time"] * execution_time_score +
            weights["priority"] * priority_score
    )

    return total_score


def create_missions(targets, aircrafts, pilots, weather, weights):
    missions = []

    for city, target_info in targets.items():
        for aircraft in aircrafts:
            for pilot in pilots:
                mission = Mission(
                    target_citi=city,
                    priority=target_info['Priority'],
                    assigned_pilot=pilot.name,
                    assigned_aircraft=aircraft.type,
                    distance=target_info['Distance'],
                    weather_conditions=weather[city]['weather_main'],
                    pilot_skill=pilot.skill_level,
                    aircraft_speed=aircraft.speed,
                    fuel_capacity=aircraft.fuel_capacity,
                    mission_fit_score=0  # this will be given after the calculation of mission score
                )
                missions.append(mission)

    # calculate max values of distance and speed
    max_distance, max_speed = get_max_values(missions)

    # calculate scores of all missions
    for mission in missions:
        mission.mission_fit_score = calculate_mission_score(mission, weights, max_distance, max_speed)

    # sort missions by score
    missions.sort(key=lambda x: x.mission_fit_score, reverse=True)

    return missions


def save_missions_to_csv(missions, csv_file_path):
    if os.path.exists(csv_file_path):# check if file already exists
        mode = 'a'
    else:
        mode = 'w'
    with open(csv_file_path, mode, newline='', encoding='utf-8') as csvfile:
        titles = [
            'target_citi', 'priority', 'assigned_pilot', 'assigned_aircraft',
            'distance', 'weather_conditions', 'pilot_skill', 'aircraft_speed',
            'fuel_capacity', 'mission_fit_score'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=titles)

        if mode == 'w':
            writer.writeheader()

        unique_combinations = set()# to prevent duble missions

        for mission in missions:
            combination = (mission.target_citi, mission.assigned_pilot, mission.assigned_aircraft)

            if combination not in unique_combinations:
                mission_dict = vars(mission).copy()
                mission_dict['mission_fit_score'] = round(mission_dict['mission_fit_score'], 2)

                writer.writerow(mission_dict)
                unique_combinations.add(combination)

    print(f"successfully")



all_missions = create_missions(dict_of_target, list_of_aircraft, list_of_pilots, dict_of_weather, weights)
csv_file_path = "missions.csv"
save_missions_to_csv(all_missions, csv_file_path)
























