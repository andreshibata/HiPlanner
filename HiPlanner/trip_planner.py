import requests

API_KEY = ''

# Function to add time
def add_time(start_time, hours_to_add):
    # Extracting AM or PM notation and converting 12-hour time to 24-hour format
    if "PM" in start_time and not start_time.startswith('12'):
        start_hour, start_minute = map(int, start_time.replace(" PM", "").split(":"))
        start_hour += 12
    else:
        start_hour, start_minute = map(int, start_time.replace(" AM", "").replace(" PM", "").split(":"))

    end_hour = start_hour + int(hours_to_add)
    end_minute = start_minute + int((hours_to_add - int(hours_to_add)) * 60)

    if end_minute >= 60:
        end_hour += 1
        end_minute -= 60

    return f"{end_hour}:{end_minute:02d}"

# Function to get travel duration using Google Maps Directions API assuming walking mode
def get_travel_duration(origin, destination):
    endpoint = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={API_KEY}"
    response = requests.get(endpoint).json()
    duration = response['routes'][0]['legs'][0]['duration']['value'] / 3600  # Convert seconds to hours
    return duration

# Function to get latitude and longitude of a location using Google Maps Geocoding API
def get_lat_lng(address):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(endpoint).json()
    location = response['results'][0]['geometry']['location']
    return location['lat'], location['lng']

# Update to the find_best_place function
def find_best_place(bias_points, query, place_type):
    best_rating = -1
    best_place = None

    for address in bias_points:
        lat, lng = get_lat_lng(address)  # Get the latitude and longitude of the bias address
        endpoint = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&locationbias=point:{lat},{lng}&key={API_KEY}&fields=formatted_address,name,rating"
        response = requests.get(endpoint).json()
        if response['candidates']:
            place_address = response['candidates'][0]['formatted_address']
            place_name = response['candidates'][0]['name']
            place_rating = response['candidates'][0].get('rating', -1)

            if place_rating > best_rating:
                best_rating = place_rating
                best_place = (place_name, place_address, place_rating)

    return best_place
def main():
    # User input
    START_TIME = input("Starting time (e.g., 9:00 AM): ")
    END_TIME = input("End time (e.g., 8:00 PM): ")
    START_POSITION = input("Starting position: ")
    END_POSITION = input("End position: ")
    ATTRACTION_1 = input("Attraction 1: ")
    ATTRACTION_2 = input("Attraction 2: ")
    LUNCH_CUISINE = input("Cuisine for lunch: ")
    DINNER_CUISINE = input("Cuisine for dinner: ")

    # Create Schedule
    schedule = [{"position": START_POSITION, "time": START_TIME}]
    
    attraction_1_address = find_best_place([START_POSITION], ATTRACTION_1, "tourist_attraction")[1]  # Only need address for attractions
    time_at_attraction_1 = add_time(schedule[-1]["time"], get_travel_duration(START_POSITION, attraction_1_address))
    schedule.append({"position": attraction_1_address, "time": time_at_attraction_1})

    potential_biases = [attraction_1_address, ATTRACTION_2]
    lunch_place_name, lunch_place_address, lunch_place_rating = find_best_place(potential_biases, LUNCH_CUISINE, "restaurant")
    time_for_lunch = add_time(time_at_attraction_1, 2)  # Assuming 2 hours at the attraction
    schedule.append({"position": f"{lunch_place_name} ({lunch_place_rating} stars) - {lunch_place_address}", "time": time_for_lunch, "event": "Lunch"})

    attraction_2_address = find_best_place([lunch_place_address], ATTRACTION_2, "tourist_attraction")[1]
    time_at_attraction_2 = add_time(add_time(time_for_lunch, 1.5), get_travel_duration(lunch_place_address, attraction_2_address))  # 1.5 hours for lunch
    schedule.append({"position": attraction_2_address, "time": time_at_attraction_2})

    potential_biases = [attraction_2_address, END_POSITION]
    dinner_place_name, dinner_place_address, dinner_place_rating = find_best_place(potential_biases, DINNER_CUISINE, "restaurant")
    time_for_dinner = add_time(time_at_attraction_2, 2)  # Assuming 2 hours at the second attraction
    schedule.append({"position": f"{dinner_place_name} ({dinner_place_rating} stars) - {dinner_place_address}", "time": time_for_dinner, "event": "Dinner"})

    end_time = add_time(time_for_dinner, 1.5)  # Assuming 1.5 hours for dinner
    schedule.append({"position": END_POSITION, "time": end_time})

    # Print Schedule
    for event in schedule:
        if 'event' in event:
            print(f"At {event['time']} have {event['event']} at {event['position']}")
        else:
            print(f"At {event['time']} be at {event['position']}")

if __name__ == "__main__":
    main()
