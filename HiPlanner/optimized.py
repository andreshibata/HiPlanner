import requests
from datetime import datetime, timedelta

API_KEY = "AIzaSyCGqvWL0jdBN8O1VrpMXImI5FWRq_YYjsQ"

def get_place_details(api_key, place_name, city):
    endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': f'{place_name}, {city}',
        'inputtype': 'textquery',
        'fields': 'place_id,geometry',
        'key': api_key
    }
    response = requests.get(endpoint_url, params=params)
    if response.status_code == 200:
        result = response.json()
        if result['candidates']:
            return result['candidates'][0]
    return None

def get_opening_hours(api_key, place_id):
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'opening_hours',
        'key': api_key
    }
    response = requests.get(endpoint_url, params=params)
    if response.status_code == 200:
        result = response.json()
        if 'result' in result and 'opening_hours' in result['result']:
            return result['result']['opening_hours']['weekday_text']
    return None

def is_open(opening_hours, time):
    if opening_hours is None:
        return True  # Assume open if no data available
    day_of_week = time.weekday()  # 0: Monday, 1: Tuesday, ..., 6: Sunday
    today_hours = opening_hours[day_of_week]
    open_time, close_time = today_hours.split(" – ")
    open_hour, open_minute = map(int, open_time[:-2].split(":"))
    close_hour, close_minute = map(int, close_time[:-2].split(":"))
    if "PM" in open_time and open_hour != 12:
        open_hour += 12
    if "PM" in close_time and close_hour != 12:
        close_hour += 12
    open_time = timedelta(hours=open_hour, minutes=open_minute)
    close_time = timedelta(hours=close_hour, minutes=close_minute)
    current_time = timedelta(hours=time.hour, minutes=time.minute)
    return open_time <= current_time <= close_time

def get_travel_duration(start, end):
    endpoint = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={API_KEY}"
    response = requests.get(endpoint).json()
    try:
        duration = response['routes'][0]['legs'][0]['duration']['value']
        return duration / 3600  # Convert seconds to hours
    except (IndexError, KeyError):
        print(f"Error: Could not get travel duration from {start} to {end}")
        return 0

def add_time(start_time, hours_to_add):
    start_hour, start_minute = map(int, start_time.split(":"))
    end_hour = start_hour + int(hours_to_add)
    end_minute = start_minute + int((hours_to_add - int(hours_to_add)) * 60)

    if end_minute >= 60:
        end_hour += 1
        end_minute -= 60

    return f"{end_hour:02d}:{end_minute:02d}"

def get_user_input():
    city = input("Enter the city you are travelling to: ")
    start_time = input("Enter the start time of your day (HH:MM): ")
    end_time = input("Enter the end time of your day (HH:MM): ")
    start_position = input("Enter your starting location: ")
    start_position = city + ", " + start_position
    end_position = input("Enter your ending location: ")
    end_position = city + ", " + end_position
    
    num_attractions = int(input("Enter the number of attractions you plan to visit: "))
    attractions = []
    time_at_attractions = {}
    for _ in range(num_attractions):
        attraction_name = input("Enter the name of the attraction: ")
        time_spent = float(input(f"How many hours do you plan to spend at {attraction_name}? "))
        attraction_name = city + ", " + attraction_name
        attractions.append(attraction_name)
        time_at_attractions[attraction_name] = time_spent

    lunch_cuisine = input("Enter your preferred cuisine for lunch: ")
    dinner_cuisine = input("Enter your preferred cuisine for dinner: ")

    return start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine, time_at_attractions, city

from itertools import permutations

def calculate_total_distance(path, city):
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += get_travel_duration(path[i], path[i+1])
    return total_distance

def sort_attractions_minimize_backtracking(start, attractions, end, city):
    min_distance = float('inf')
    min_path = None
    
    for perm in permutations(attractions):
        path = [start] + list(perm) + [end]
        distance = calculate_total_distance(path, city)
        if distance < min_distance:
            min_distance = distance
            min_path = path
            
    # Return the sorted attractions only, not including start and end
    return min_path[1:-1]

def find_nearest_location(current_location, locations):
    min_duration = float('inf')
    nearest_location = None
    
    for location in locations:
        travel_duration = get_travel_duration(current_location, location[0])
        if travel_duration < min_duration:
            min_duration = travel_duration
            nearest_location = location
            
    return nearest_location

def create_schedule(start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine):
    current_time = start_time
    schedule = []
    
    # Add start position to schedule
    schedule.append(("Start at", start_position, current_time))
    
    # Visit attractions with minimal backtracking
    remaining_attractions = attractions.copy()
    while remaining_attractions:
        nearest_attraction = find_nearest_location(schedule[-1][1], remaining_attractions)
        if nearest_attraction:
            travel_time = get_travel_duration(schedule[-1][1], nearest_attraction[0])
            current_time = add_time(current_time, travel_time)
            schedule.append(("Travel to", nearest_attraction[0], current_time))
            
            # Spend time at the attraction
            current_time = add_time(current_time, nearest_attraction[1])
            schedule.append(("Spend", nearest_attraction[1], "hours at", nearest_attraction[0], ", leave at", current_time))
            
            remaining_attractions.remove(nearest_attraction)
    
    # Add lunch and dinner to schedule
    # Assume lunch is around 12:00 PM and dinner around 7:00 PM
    lunch_time = "12:00"
    dinner_time = "19:00"
    
    if start_time < lunch_time < end_time:
        schedule.append(("Have lunch at", lunch_cuisine, "restaurant around", lunch_time))
        current_time = add_time(lunch_time, 1.5)  # Assume 1.5 hours for lunch
    
    if start_time < dinner_time < end_time:
        schedule.append(("Have dinner at", dinner_cuisine, "restaurant around", dinner_time))
        current_time = add_time(dinner_time, 1.5)  # Assume 1.5 hours for dinner
    
    # Travel to end position
    travel_time_to_end = get_travel_duration(schedule[-1][1], end_position)
    current_time = add_time(current_time, travel_time_to_end)
    schedule.append(("Travel to", end_position, ", arrive at", current_time))
    
    # Return the final schedule
    return schedule

def calculate_schedule(start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine, time_at_attractions, google_api_key, city):
    current_time = start_time
    schedule = []

    # Sort attractions to minimize backtracking
    attractions = sort_attractions_minimize_backtracking(start_position, attractions, end_position, city)
    current_position = start_position
    
    for i, attraction in enumerate(attractions):
        # Get travel duration to the next attraction
        travel_duration = get_travel_duration(current_position, attraction)
        arrival_time = current_time + timedelta(hours=travel_duration)
        
        # Check if the attraction is open
        place_details = get_place_details(google_api_key, attraction, city)
        opening_hours = get_opening_hours(google_api_key, place_details['place_id'])
        
        if not is_open(opening_hours, arrival_time):
            print(f"Warning: {attraction} may be closed when you arrive. Please check the opening hours.")
        
        # Add travel and visit to schedule
        schedule.append((current_position, attraction, current_time, arrival_time))
        visit_duration = time_at_attractions.get(attraction, 1)  # Default to 1 hour if not specified
        current_time = arrival_time + timedelta(hours=visit_duration)
        current_position = attraction
    
    # Add lunch
    lunch_place_details = get_place_details(google_api_key, lunch_cuisine, city)
    travel_duration = get_travel_duration(current_position, lunch_place_details['formatted_address'])
    arrival_time = current_time + timedelta(hours=travel_duration)
    schedule.append((current_position, lunch_cuisine, current_time, arrival_time))
    lunch_duration = 1.5
    current_time = arrival_time + timedelta(hours=lunch_duration)
    current_position = lunch_place_details['formatted_address']

    # Continue with remaining attractions and dinner in a similar manner...
    # Make sure to check opening hours and update the schedule accordingly

    return schedule

def print_schedule(schedule):
    for event in schedule:
        print(*event)

if __name__ == "__main__":
    start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine, time_at_attractions, city = get_user_input()
    google_api_key = 'AIzaSyCGqvWL0jdBN8O1VrpMXImI5FWRq_YYjsQ'
    
    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")

    sorted_attractions = sort_attractions_minimize_backtracking(start_position, attractions, end_position, city)
    schedule = calculate_schedule(start_time, end_time, start_position, end_position, sorted_attractions, lunch_cuisine, dinner_cuisine, time_at_attractions, google_api_key, city)
    
    for item in schedule:
        print(item)