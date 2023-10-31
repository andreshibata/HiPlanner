import googlemaps
from datetime import datetime, timedelta
import random

# Set your Google API Key here
api_key = "AIzaSyDKxenyjtV1kqqta51eD1mfLz4knKE0Y2Q"

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=api_key)

def get_user_input():
    start_time = input("Enter the start time of your trip (HH:MM): ")
    end_time = input("Enter the end time of your trip (HH:MM): ")
    start_position = input("Enter the start position of your trip: ")
    end_position = input("Enter the end position of your trip: ")
    city = input("Enter the city of your trip: ")

    num_attractions = int(input("Enter the number of attractions you want to visit: "))
    attractions = []
    time_at_attractions = {}
    for i in range(num_attractions):
        attraction = input(f"Enter the name of attraction {i+1}: ")
        time = float(input(f"Enter the time you want to spend at {attraction} in hours: "))
        attractions.append(attraction)
        time_at_attractions[attraction] = time
 
    lunch_cuisine = input("Enter the cuisine you prefer for lunch: ")
    dinner_cuisine = input("Enter the cuisine you prefer for dinner: ")

    return start_time, end_time, start_position, end_position, attractions, time_at_attractions, lunch_cuisine, dinner_cuisine, city

def get_travel_duration(api_key, origin, destination):
    gmaps = googlemaps.Client(key=api_key)
    now = datetime.now()
    directions_result = gmaps.directions(origin, destination, mode="transit", departure_time=now)

    # Extracting the travel duration
    duration = directions_result[0]['legs'][0]['duration']['value'] / 60  # Convert from seconds to minutes
    return duration

def get_opening_hours(api_key, place_id):
    gmaps = googlemaps.Client(key=api_key)
    place_result = gmaps.place(place_id=place_id)

    # Extracting opening hours
    opening_hours = place_result['result'].get('opening_hours')
    if opening_hours:
        # Assuming you want to know if it's open right now
        is_open_now = opening_hours['open_now']
        return is_open_now
    else:
        return None


def get_food_spot(api_key, cuisine, location):
    gmaps = googlemaps.Client(key=api_key)
    # Searching for a restaurant with specified cuisine near the given location
    places_result = gmaps.places(query=f"{cuisine} restaurant", location=location, radius=5000)

    # Extracting the top result (you could also choose randomly or based on rating)
    if places_result['results']:
        top_result = places_result['results'][0]
        name = top_result['name']
        address = top_result['vicinity']
        rating = top_result['rating']
        return name, address, rating
    else:
        return None, None, None


def sort_attractions_minimize_backtracking(start, attractions, end, city):
    sorted_attractions = []
    current_position = start

    while attractions:
        closest_attraction = min(attractions, key=lambda x: get_travel_duration(current_position, x, city))
        sorted_attractions.append(closest_attraction)
        attractions.remove(closest_attraction)
        current_position = closest_attraction

    return sorted_attractions

def add_time(time_str, hours):
    time_obj = datetime.strptime(time_str, "%H:%M")
    final_time = time_obj + timedelta(hours=hours)
    return final_time.strftime("%H:%M")

def create_schedule(start_time, end_time, start_position, end_position, attractions, time_at_attractions, lunch_cuisine, dinner_cuisine, city):
    # Convert start and end times to datetime objects
    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")
    
    # Sort attractions to minimize backtracking
    attractions = sort_attractions_minimize_backtracking(start_position, attractions, end_position, city)
    
    # Initialize variables
    current_time = start_time
    current_position = start_position
    schedule = []

    # Schedule visits to attractions
    for attraction in attractions:
        travel_duration = get_travel_duration(current_position, attraction, city)
        if travel_duration is None:
            print(f"Error: Could not get travel duration from {current_position} to {attraction}")
            return None
        
        # Check if attraction has opening hours
        opening_hours = get_opening_hours(attraction, city)
        if opening_hours:
            # Schedule visit during opening hours
            visit_start = max(current_time + timedelta(hours=travel_duration), opening_hours['open'])
            visit_end = visit_start + timedelta(hours=time_at_attractions[attraction])  # Use user-specified visit duration
            if visit_end > opening_hours['close']:
                print(f"Warning: Not enough time to visit {attraction} during opening hours.")
        else:
            # Schedule visit without considering opening hours
            visit_start = current_time + timedelta(hours=travel_duration)
            visit_end = visit_start + timedelta(hours=time_at_attractions[attraction])  # Use user-specified visit duration

        schedule.append((attraction, visit_start.strftime("%H:%M"), visit_end.strftime("%H:%M")))
        current_time = visit_end
        current_position = attraction

    # Schedule lunch
    lunch_spot = get_food_spot(lunch_cuisine, city)
    travel_duration = get_travel_duration(current_position, lunch_spot, city)
    if travel_duration is None:
        print(f"Error: Could not get travel duration from {current_position} to lunch spot")
        return None
    lunch_start = current_time + timedelta(hours=travel_duration)
    lunch_end = lunch_start + timedelta(hours=1.5)  # Assume 1.5 hours for lunch
    schedule.append(("Lunch at " + lunch_spot, lunch_start.strftime("%H:%M"), lunch_end.strftime("%H:%M")))
    current_time = lunch_end
    current_position = lunch_spot

    # Schedule visits to remaining attractions if there are any
    for attraction in attractions:
        travel_duration = get_travel_duration(current_position, attraction, city)
        if travel_duration is None:
            print(f"Error: Could not get travel duration from {current_position} to {attraction}")
            return None
        visit_start = current_time + timedelta(hours=travel_duration)
        visit_end = visit_start + timedelta(hours=time_at_attractions[attraction])  # Use user-specified visit duration
        schedule.append((attraction, visit_start.strftime("%H:%M"), visit_end.strftime("%H:%M")))
        current_time = visit_end
        current_position = attraction

    # Schedule dinner
    dinner_spot = get_food_spot(dinner_cuisine, city)
    travel_duration = get_travel_duration(current_position, dinner_spot, city)
    if travel_duration is None:
        print(f"Error: Could not get travel duration from {current_position} to dinner spot")
        return None
    dinner_start = current_time + timedelta(hours=travel_duration)
    dinner_end = dinner_start + timedelta(hours=1.5)  # Assume 1.5 hours for dinner
    schedule.append(("Dinner at " + dinner_spot, dinner_start.strftime("%H:%M"), dinner_end.strftime("%H:%M")))
    current_time = dinner_end
    current_position = dinner_spot

    # Travel to end position
    travel_duration = get_travel_duration(current_position, end_position, city)
    if travel_duration is None:
        print(f"Error: Could not get travel duration from {current_position} to {end_position}")
        return None
    arrival_end = current_time + timedelta(hours=travel_duration)
    schedule.append(("Travel to " + end_position, current_time.strftime("%H:%M"), arrival_end.strftime("%H:%M")))

    # Check if total duration exceeds available time
    if arrival_end > end_time:
        print("Warning: The entire trip will take more time than planned. Consider removing some attractions to fit the schedule.")

    return schedule

def main():
    # Get user input
    start_time, end_time, start_position, end_position, attractions, time_at_attractions, lunch_cuisine, dinner_cuisine, city = get_user_input()
    
    # Create the schedule
    schedule = create_schedule(start_time, end_time, start_position, end_position, attractions, time_at_attractions, lunch_cuisine, dinner_cuisine, city)

    # Print the schedule
    if schedule:
        print("\nYour Schedule:")
        for event in schedule:
            print(f"{event[0]}: {event[1]} - {event[2]}")
    else:
        print("Could not create schedule.")

if __name__ == "__main__":
    main()
