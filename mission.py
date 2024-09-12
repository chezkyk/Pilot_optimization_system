class Mission:
    def __init__(self, target_citi, priority, assigned_pilot, assigned_aircraft, distance, weather_conditions,pilot_skill, aircraft_speed,fuel_capacity, mission_fit_score):
        self.target_citi = target_citi
        self.priority = priority
        self.assigned_pilot = assigned_pilot
        self.assigned_aircraft = assigned_aircraft
        self.distance = distance
        self.weather_conditions = weather_conditions
        self.pilot_skill = pilot_skill
        self.aircraft_speed = aircraft_speed
        self.fuel_capacity = fuel_capacity
        self.mission_fit_score = mission_fit_score
