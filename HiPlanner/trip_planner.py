import requests
from datetime import datetime, timedelta

API_KEY = "AIzaSyCGqvWL0jdBN8O1VrpMXImI5FWRq_YYjsQ"

def get_travel_duration(start, end, mode="walking"):
    endpoint = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&mode={mode}&key={API_KEY}"
    response = requests.get(endpoint).json()
    try:
        duration = response['routes'][0]['legs'][0]['duration']['value']
        return duration / 3600  # Convert seconds to hours
    except IndexError:
        print(f"Error: Could not get travel duration from {start} to {end}")
        return 0

def add_time(start_time, hours_to_add):
    start_hour, start_minute = map(int, start_time.split(":"))
    end_hour = start_hour + int(hours_to_add)
    end_minute = start_minute + int((hours_to_add - int(hours_to_add)) * 60)

    if end_minute >= 60:
        end_hour += 1
        end_minute -= 60

    if end_hour >= 24:
        end_hour -= 24

    return f"{end_hour:02d}:{end_minute:02d}"

def calculate_schedule(start_time, end_time, start_position, end_position, attractions_with_time, lunch_cuisine, dinner_cuisine):
    current_time = start_time
    total_duration = 0

    # Calculate travel durations and visit times at attractions
    for attraction, time_at_attraction in attractions_with_time:
        travel_duration = get_travel_duration(start_position, attraction)
        total_duration += travel_duration + time_at_attraction
        current_time = add_time(current_time, travel_duration)
        print(f"Travel to {attraction}, arrive at {current_time}")
        
        current_time = add_time(current_time, time_at_attraction)
        print(f"Spend {time_at_attraction} hours at {attraction}, leave at {current_time}")

        start_position = attraction  # Update start position for next iteration

    # Lunch
    lunch_place = find_best_place(start_position, lunch_cuisine)
    travel_duration = get_travel_duration(start_position, lunch_place)
    current_time = add_time(current_time, travel_duration)
    print(f"Have lunch at {lunch_place} at {current_time}")
    total_duration += travel_duration + 1.5  # Assuming 1.5 hours for lunch
    current_time = add_time(current_time, 1.5)

    # Calculate durations for dinner and travel to end position
    dinner_place = find_best_place(start_position, dinner_cuisine)
    travel_duration_to_dinner = get_travel_duration(start_position, dinner_place)
    current_time = add_time(current_time, travel_duration_to_dinner)
    print(f"Have dinner at {dinner_place} at {current_time}")
    total_duration += travel_duration_to_dinner + 1.5  # Assuming 1.5 hours for dinner
    current_time = add_time(current_time, 1.5)

    travel_duration_to_end = get_travel_duration(dinner_place, end_position)
    current_time = add_time(current_time, travel_duration_to_end)
    print(f"Travel to {end_position}, arrive at {current_time}")
    total_duration += travel_duration_to_end

    # Check if total duration exceeds available time
    start_time_obj = datetime.strptime(start_time, "%H:%M")
    end_time_obj = datetime.strptime(end_time, "%H:%M")
    available_hours = (end_time_obj - start_time_obj).seconds / 3600

    if total_duration > available_hours:
        print("Warning: The entire trip will take more time than planned.")
        print("Consider removing some attractions to fit the schedule.")
        remove_attraction = input("Would you like to remove an attraction? (yes/no): ")
        if remove_attraction.lower() == 'yes':
            print("Available attractions:")
            for i, (attraction, time_at_attraction) in enumerate(attractions_with_time, start=1):
                print(f"{i}. {attraction}")
            attraction_to_remove = int(input("Enter the number of the attraction to remove: "))
            del attractions_with_time[attraction_to_remove - 1]
            return calculate_schedule(start_time, end_time, start_position, end_position, attractions_with_time, lunch_cuisine, dinner_cuisine)

    # If the trip fits the schedule or user chooses not to remove attractions
    return attractions_with_time, total_duration

def find_best_place(location, query):
    endpoint = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&locationbias=point:{location}&key={API_KEY}&fields=formatted_address,name,rating"
    response = requests.get(endpoint).json()
    if response['candidates']:
        place = response['candidates'][0]
        return f"{place['name']} ({place['formatted_address']}, Rating: {place.get('rating', 'N/A')})"
    return "N/A"

def get_user_input():
    city = input("Enter the city you are traveling to: ")
    start_time = input("Enter start time (HH:MM): ")
    end_time = input("Enter end time (HH:MM): ")
    start_position = input("Enter start position: ") + ", " + city
    end_position = input("Enter end position: ") + ", " + city
    num_attractions = int(input("Enter number of attractions: "))
    attractions = []
    for i in range(num_attractions):
        attraction = input(f"Enter attraction {i+1}: ") + ", " + city
        time_at_attraction = float(input(f"How much time (in hours) do you plan to spend at {attraction}? "))
        attractions.append((attraction, time_at_attraction))
    lunch_cuisine = input("Enter preferred cuisine for lunch: ") + " restaurant, " + city
    dinner_cuisine = input("Enter preferred cuisine for dinner: ") + " restaurant, " + city
    return start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine

if __name__ == "__main__":
    start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine = get_user_input()
    calculate_schedule(start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine)
