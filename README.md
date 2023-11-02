# HiPlanner
A Day Trip Planner that allows you to automatically generate an itinerary and maps for your next day trip.

HiPlanner uses the Google Maps API to calculate the routes for the attractions you want to visit, and to find restaurants based on your preferences, and then uses the reportlabs API to generate PDF files for your itinerary.

The code was created with the assistance of ChatGPT.

## User Stories
- Me, from Boston MA have a friend over visitng from New York, NY, and would like to easily plan his day trip
- Me, a traveler spending a day in NYC would like to ensure that I can walk to all my inteneded attractions before my train back home departs
- Me, a traveler, would like to select the restaurant cusines from a city I will spend a day with without performing much research
- I would like my schedule to be generated in such a way that I know when to leave a place, and what time I will be arriving at the next destination
- I would like to make sure that my automatically generated schedule does not have lunch and dinner right after each other
- I would like to be able to suggest an amount of time that I would like to spend in an attraction


## Features
- Generate a travel itinerary with a detailed schedule.
- Find attractions and restaurants based on user preferences.
- Calculate travel durations and distances between locations.
- Generate PDF files for the travel itinerary and map routes.
- Provide links to view routes on Google Maps.

## Requirements
- Python 3.11
- Google API Key with access to the Directions, Places, and Maps Static APIs
- Required Python packages: `requests`, `reportlab`, `io`, `datetime`, `os`

This project was created using Python 3.11. Implementation was not tested and is not supported for any other python version.

## Setup

1. Clone the repository by performing the follow on your terminal:
```
cd *your desired directory*
git clone https://github.com/andreshibata/HiPlanner.git
```

2. Install the required packages:
```
pip install os
pip install datetime 
pip install requests
pip install reportlabs
pip install io
```
3. Set up your Google API Key:

On the file trip_planner.py, replace `"Your Google API Key"` in the script with your actual Google API Key.

## Usage

1. Run the script:

2. Follow the prompts to enter your travel details.

3. The application will generate PDF files for the travel itinerary (`travel_itinerary.pdf`) and map routes (`map_routes.pdf`).

4. Open the PDF files to view your detailed travel plan and map routes.

## Example Run:

The following prompt generated the itineraries found on the Sample Itinerary folder.

```
Enter the city you are traveling to: Boston
Enter start time (HH:MM): 08:00
Enter end time (HH:MM): 20:00
Enter start position: South Station
Enter end position: South Station
Enter number of attractions: 3
Enter attraction 1: Chinatown KTV
How much time (in hours) do you plan to spend at Chinatown KTV, Boston? 2
Enter attraction 2: MFA
How much time (in hours) do you plan to spend at MFA, Boston? 2
Enter attraction 3: Boston University
How much time (in hours) do you plan to spend at Boston University, Boston? 2
Enter preferred cuisine for lunch: Mexican
Enter preferred cuisine for dinner: Sushi
PDF generated: travel_itinerary.pdf
Schedule PDF generated: travel_itinerary.pdf
PDF generated: map_routes.pdf
Map routes PDF generated: map_routes.pdf
```

## Future Plans and Updates



The score is calculated using the following formula:

```math
\text{score} = \left( \frac{(e_t + t + d_t) \cdot a_t}{3 \times 86400 \times 86400} \right) \cdot 50 + \left( \frac{r}{5} \right) \cdot 30 + \left( \frac{24 - b_h + 1}{24} \right) \cdot 20
```

where:
- \( e_t, t, d_t, a_t \) are time values in seconds, and can range from 0 to 86400 (the number of seconds in a day).
  - e_t = End Time, the time in seconds when your trip ends
  - t = Current Time of the day in seconds
  - d_t = Distance Time, the time in seconds that take from the user's current position, until the restaurante candidate
  - a_t = Average Time, the average time spent in the restaurant
- \( b_h \) is a ranking that ranges from 1 to 24.
  - The ranking of the time of arrival of the restaurant in its "busy hours", with the busiest hour being 1, and the least busy hour being 24 \b_h should actually be a function b_h(e_t+d_t)
- \( r \) is a rating value that can range from 0 to 5.
  - The rating of the restaurant
