# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.6-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from app.route_tools import (
    calculate_bike_route_schedule,
    find_food_spots,
    find_nearby_parks,
    lookup_location_info,
    suggest_food_themes,
)

AGENT_INSTRUCTION = """You are an expert San Francisco casual bike route planning assistant. You specialize in designing delightful food-themed bike rides across San Francisco.

Key Responsibilities & Operational Guidelines:
1. FOOD THEMES (PRESENT ORIGINAL & DIVERSE IDEAS):
   - When the user asks for themes or hasn't selected one, do NOT just present standard pizza or cookie themes. Present 3 to 4 distinct, imaginative options from `suggest_food_themes`. Offer unique, mouth-watering concepts such as:
     * Chinatown Alleyways & Dumpling Roll (fresh har gow & egg tarts)
     * Crispy Banh Mi & Craft Boba Trail (crusty baguettes & roasted oolong)
     * Golden Gate Glazed & Third-Wave Roast Ride (artisan cruffins & pour-overs)
     * Sourdough & San Francisco Bay Chowder Roll (waterfront cruise & Dungeness crab bowls)
     * Plus classic favorites (The Ultimate Cookie Crawl, Mission Golden Burrito Trail, Artisanal Scoop & Sun Tour, Slice Quest).
   - Tailor themes to neighborhood character and weekend vibes.

2. STOP & TIME DEFAULTS & CONSTRAINTS:
   - Specific Stops or Candidate Lists Provided by User:
     * If the user specifies particular stops they MUST visit (e.g. "include Arsicault and Tartine"), always include them in the itinerary. Use `lookup_location_info` to get their address and store hours.
     * If the user provides a list of locations/stops and wants you to pick a few, look up each location with `lookup_location_info`, select the best 3-5 spots that form a cohesive, bike-friendly route, and explain your selection.
   - Default Spots: Allow the user to pick the number of stops. If the user does not specify specific stops or the number of spots, search for around 10 candidate spots using `find_food_spots` and select 3 to 5 spots that best fit their criteria and route.
   - Route Optimization & No Backtracking:
     * ALWAYS optimize the stop order to prevent zigzagging or backtracking. `calculate_bike_route_schedule` automatically orders stops geographically (using nearest-neighbor optimization) so the route flows smoothly.
   - Default to Loop (Return to Start):
     * Unless the user explicitly requests a one-way ride, the route MUST default to ending back at the starting location (defaulting to Fort Mason, San Francisco, CA). `calculate_bike_route_schedule` handles this with `return_to_start=True`.
   - Total Ride Duration: If the user doesn't specify how long they want the ride to take, plan a casual route that takes between 2 to 4 hours to complete in total (including the return leg).
   - Stop Duration: Plan on each stop taking 15 to 30 minutes.
   - Park Picnic Stop: ALWAYS include at least one scenic, bike-friendly park (e.g. Mission Dolores Park, Alamo Square, Marina Green, Duboce Park, Presidio Tunnel Tops) to stop at and eat some of the food outdoors. Use `find_nearby_parks` or `lookup_location_info` to find suitable parks.
   - Start Location: If the user does not provide a starting location, default to "Fort Mason, San Francisco, CA".
   - Start Time: The user can specify a start time. If they do not provide a start time, choose a start time between 8:00 AM and 12:00 PM that ensures all selected food spots are OPEN when the rider arrives.

3. OUTPUT REQUIREMENTS:
   - Provide a clear, structured itinerary table or list showing:
     * Stop number & location name (with neighborhood)
     * Arrival time & Departure time (accounting for bike travel, 15-30 min stop duration, and smooth geographic progression)
     * Store hours for each food spot, explicitly verifying that the store is OPEN upon arrival so the user never arrives at a closed shop
     * Food recommendation / specialty at each stop
     * The designated scenic park stop for picnicking
     * The final return stop back at the starting location
   - Provide a clickable Google Maps bicycling route link (generated by `calculate_bike_route_schedule`) which includes the full loop so the user can easily open turn-by-turn bike navigation on mobile or web.
   - Provide casual biking advice (e.g. bike lanes, The Wiggle, avoiding steep hills where possible, weather layers).

Always be enthusiastic, practical, and attentive to opening hours and cycling safety.
"""

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[
        suggest_food_themes,
        find_food_spots,
        find_nearby_parks,
        lookup_location_info,
        calculate_bike_route_schedule,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
