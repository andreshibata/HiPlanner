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

1. Clone the repository:

On your terminal:
```
git clone https://github.com/andreshibata/HiPlanner.git
```
```
pip install requests
pip install reportlabs
``` 
