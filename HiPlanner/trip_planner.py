import requests
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import requests
from io import BytesIO
import os


API_KEY = "Your Google API Key"

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

def find_best_place(location, query):
    endpoint = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&locationbias=point:{location}&key={API_KEY}&fields=formatted_address,name,rating"
    response = requests.get(endpoint).json()
    if response['candidates']:
        place = response['candidates'][0]
        return f"{place['name']} ({place['formatted_address']}, Rating: {place.get('rating', 'N/A')})"
    return "N/A"

def find_attraction_nearby(location, query="attraction"):
    endpoint = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius=1000&keyword={query}&key={API_KEY}"
    response = requests.get(endpoint).json()
    if response['results']:
        place = response['results'][0]
        return f"{place['name']} ({place['vicinity']})"
    return "No attractions found within walking distance."

def is_valid_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

from datetime import datetime, timedelta

from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def calculate_schedule(start_time, end_time, start_position, end_position, attractions_with_time, lunch_cuisine, dinner_cuisine, pdf_filename="travel_itinerary.pdf"):
    start_time_obj = datetime.strptime(start_time, "%H:%M")
    end_time_obj = datetime.strptime(end_time, "%H:%M")
    
    current_time_obj = start_time_obj
    total_duration = timedelta()
    last_activity_location = start_position

    remaining_attractions = attractions_with_time.copy()
    visited_attractions = []

    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    def add_paragraph(doc, text, style):
        para = Paragraph(text, style)
        doc.append(para)
        doc.append(Spacer(1, 12))

    add_paragraph(story, f"Leaving {start_position} at {start_time}", styles['Heading2'])

    def visit_attraction(attraction, time_at_attraction, attraction_type="Attraction"):
        nonlocal current_time_obj, total_duration, last_activity_location, visited_attractions
        travel_duration = get_travel_duration(last_activity_location, attraction)
        travel_duration_obj = timedelta(hours=travel_duration)
        activity_duration_obj = timedelta(hours=time_at_attraction)

        arrival_time = current_time_obj + travel_duration_obj
        add_paragraph(story, f"Travel to {attraction} ({attraction_type}) which will take approximately {travel_duration:.2f} hours, arrive at {arrival_time.strftime('%H:%M')}", styles['BodyText'])

        current_time_obj += travel_duration_obj + activity_duration_obj
        total_duration += travel_duration_obj + activity_duration_obj
        end_time_str = current_time_obj.strftime('%H:%M')

        add_paragraph(story, f"Spend {time_at_attraction} hours at {attraction}, leave at {end_time_str}", styles['BodyText'])

        visited_attractions.append((attraction, time_at_attraction, arrival_time.strftime('%H:%M')))
        last_activity_location = attraction

    # Visit the first attraction
    if remaining_attractions:
        nearest_attraction, time_at_attraction, _ = min(
            ((attraction, time_at_attraction, _) for attraction, time_at_attraction, _ in remaining_attractions),
            key=lambda x: get_distance(last_activity_location, x[0]),
            default=(None, float('inf'), None)
        )
        if nearest_attraction:
            visit_attraction(nearest_attraction, time_at_attraction)
            remaining_attractions.remove((nearest_attraction, time_at_attraction, None))

    # Handle lunch after the first attraction
    lunch_place = find_best_place(last_activity_location, lunch_cuisine)
    visit_attraction(lunch_place, 1.5, "Lunch")  # Assuming 1.5 hours for lunch

    # Visit the rest of the attractions
    for attraction, time_at_attraction, _ in remaining_attractions:
        visit_attraction(attraction, time_at_attraction)

    # Handle dinner
    dinner_place = find_best_place(last_activity_location, dinner_cuisine)
    visit_attraction(dinner_place, 1.5, "Dinner")  # Assuming 1.5 hours for dinner

    # Travel to end position
    travel_duration = get_travel_duration(last_activity_location, end_position)
    travel_duration_obj = timedelta(hours=travel_duration)
    current_time_obj += travel_duration_obj
    total_duration += travel_duration_obj
    add_paragraph(story, f"Travel to {end_position}, arrive at {current_time_obj.strftime('%H:%M')}", styles['BodyText'])

    if current_time_obj > end_time_obj:
        add_paragraph(story, "Warning: The entire trip will take more time than planned. Consider removing some attractions to fit the schedule.", styles['BodyText'])

    # Generate PDF
    doc.build(story)
    print(f"PDF generated: {pdf_filename}")

    return visited_attractions

def add_paragraph(doc, text, style):
    para = Paragraph(text, style)
    doc.append(para)
    doc


def get_distance(start, end, mode="walking"):
    endpoint = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={start}&destinations={end}&mode={mode}&key={API_KEY}"
    response = requests.get(endpoint).json()

    try:
        distance = response['rows'][0]['elements'][0]['distance']['value']
        return distance / 1000  # Convert meters to kilometers
    except (IndexError, KeyError):
        print(f"Error: Could not get distance from {start} to {end}")
        return float('inf')  # Return a large value to indicate an unreachable destination

def get_valid_input(prompt, validation_func, error_message="Invalid input. Please try again.", allow_blank=False):
    while True:
        user_input = input(prompt)
        if allow_blank and user_input == "":
            return user_input
        elif validation_func(user_input):
            return user_input
        else:
            print(error_message)

def is_valid_time(time_string):
    try:
        datetime.strptime(time_string, "%H:%M")
        return True
    except ValueError:
        return False

def is_valid_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def get_user_input():
    city = input("Enter the city you are traveling to: ")
    start_time = get_valid_input("Enter start time (HH:MM): ", is_valid_time)
    end_time = get_valid_input("Enter end time (HH:MM): ", is_valid_time)
    start_position = input("Enter start position: ") + ", " + city
    end_position = input("Enter end position: ") + ", " + city
    num_attractions = int(get_valid_input("Enter number of attractions: ", is_valid_int))
    attractions = []
    for i in range(num_attractions):
        attraction = input(f"Enter attraction {i+1}: ") + ", " + city
        time_at_attraction = float(get_valid_input(f"How much time (in hours) do you plan to spend at {attraction}? ", is_valid_float))
        attractions.append((attraction, time_at_attraction, None))  # No earliest start time
    lunch_cuisine = input("Enter preferred cuisine for lunch: ") + " restaurant, " + city
    dinner_cuisine = input("Enter preferred cuisine for dinner: ") + " restaurant, " + city
    return start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine


def generate_map_image(start, end, mode="walking", width=500, height=500):
    # Step 1: Get the walking route from the Directions API
    directions_endpoint = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&mode={mode}&key={API_KEY}"
    directions_response = requests.get(directions_endpoint).json()
    try:
        polyline = directions_response['routes'][0]['overview_polyline']['points']
    except (IndexError, KeyError):
        print("Error: Could not get walking route from Directions API.")
        return None

    # Step 2: Use the encoded polyline to draw the path on the static map
    map_endpoint = f"https://maps.googleapis.com/maps/api/staticmap?size={width}x{height}&maptype=roadmap&markers=color:red|{start}&markers=color:blue|{end}&path=enc:{polyline}&key={API_KEY}"
    map_response = requests.get(map_endpoint)
    if map_response.status_code == 200:
        return BytesIO(map_response.content)
    else:
        print(f"Error: Could not generate map image. Status code: {map_response.status_code}")
        return None

def add_paragraph(doc, text, style):
    para = Paragraph(text, style)
    doc.append(para)
    doc.append(Spacer(1, 12))

def open_google_maps(locations, mode="walking", pdf_filename="travel_itinerary.pdf"):
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    for i in range(len(locations) - 1):
        start = locations[i]
        end = locations[i + 1]
        
        # Ensure that the start and end are formatted as strings, not tuples
        if isinstance(start, tuple):
            start = start[0]
        if isinstance(end, tuple):
            end = end[0]
        
        url = f"https://www.google.com/maps/dir/?api=1&origin={start}&destination={end}&travelmode={mode}"

        add_paragraph(story, f"Route from {start} to {end}", styles['Heading2'])
        add_paragraph(story, f"<a href='{url}'>View on Google Maps</a>", styles['BodyText'])

        map_image = generate_map_image(start, end, mode)
        if map_image:
            img = Image(map_image, width=500, height=500)
            story.append(img)
            story.append(Spacer(1, 12))
        else:
            add_paragraph(story, "Map image could not be generated.", styles['BodyText'])

    doc.build(story)
    print(f"PDF generated: {pdf_filename}")

if __name__ == "__main__":
    # Get user input
    start_time, end_time, start_position, end_position, attractions, lunch_cuisine, dinner_cuisine = get_user_input()

    # Calculate the schedule and get visited attractions
    pdf_filename="travel_itinerary.pdf"
    visited_attractions = calculate_schedule(
    start_time, end_time, start_position, end_position, 
    attractions, lunch_cuisine, dinner_cuisine, pdf_filename)
    print(f"Schedule PDF generated: {pdf_filename}")


    # Prepare a list of locations for Google Maps
    locations = [start_position] + [attraction for attraction in visited_attractions] + [end_position]

    # Generate PDF for the map routes
    maps_pdf_filename = "map_routes.pdf"
    open_google_maps(locations, pdf_filename=maps_pdf_filename)
    print(f"Map routes PDF generated: {maps_pdf_filename}")