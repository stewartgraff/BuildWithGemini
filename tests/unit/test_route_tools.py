# Copyright 2026 Google LLC

import pytest
from app.route_tools import (
    suggest_food_themes,
    find_food_spots,
    find_nearby_parks,
    build_google_maps_bike_url,
    calculate_bike_route_schedule,
)

def test_suggest_food_themes():
    result = suggest_food_themes()
    assert result["status"] == "success"
    themes = result["themes"]
    assert len(themes) >= 4
    theme_ids = [t["id"] for t in themes]
    assert "chocolate_chip_cookie" in theme_ids
    assert "burrito" in theme_ids
    assert "pizza" in theme_ids
    assert "ice cream" in theme_ids or "ice_cream" in theme_ids

def test_find_food_spots_cookies():
    result = find_food_spots(theme="chocolate chip cookie")
    assert result["total_found"] >= 5
    assert len(result["candidate_spots"]) >= 5
    first_spot = result["candidate_spots"][0]
    assert "name" in first_spot
    assert "hours" in first_spot
    assert "specialty" in first_spot

def test_find_nearby_parks():
    result = find_nearby_parks()
    parks = result["parks"]
    assert len(parks) >= 5
    park_names = [p["name"] for p in parks]
    assert "Mission Dolores Park" in park_names

def test_build_google_maps_bike_url():
    url = build_google_maps_bike_url(
        origin="Fort Mason, San Francisco, CA",
        stops=["397 Arguello Blvd, SF", "Dolores St & 19th St, SF"],
    )
    assert "travelmode=bicycling" in url
    assert "Fort+Mason" in url or "Fort%20Mason" in url

def test_calculate_bike_route_schedule():
    candidate_spots = [
        {
            "name": "Jane the Bakery",
            "address": "1839 Geary Blvd, San Francisco, CA 94115",
            "hours": "Daily 7:00 AM - 4:00 PM",
            "open_time": "07:00",
            "close_time": "16:00",
            "type": "food",
        },
        {
            "name": "Alamo Square Park",
            "address": "Steiner St & Hayes St, San Francisco, CA 94117",
            "hours": "Daily 5:00 AM - 12:00 AM",
            "open_time": "05:00",
            "close_time": "23:59",
            "type": "park",
        },
    ]

    schedule = calculate_bike_route_schedule(
        start_location="Fort Mason, San Francisco, CA",
        start_time="09:00 AM",
        stops=candidate_spots,
        stop_duration_minutes=20,
    )
    assert schedule["number_of_stops"] == 2
    assert "google_maps_route_url" in schedule
    assert len(schedule["itinerary"]) == 4  # Start + 2 stops + Loop Finish back at start
    assert schedule["itinerary"][1]["is_open_at_arrival"] is True
    assert schedule["itinerary"][-1]["name"] == "Fort Mason, San Francisco, CA (Loop Finish)"


def test_optimize_stops_order_no_backtracking():
    from app.route_tools import optimize_stops_order

    # Start at Fort Mason (North SF)
    # Give candidate stops in intentionally backwards/zigzag order:
    # Mission Dolores (far South), Jane Bakery (mid North), Tartine (far South)
    input_stops = [
        {"name": "Tartine Bakery", "address": "600 Guerrero St, San Francisco, CA"},
        {"name": "Jane the Bakery", "address": "1839 Geary Blvd, San Francisco, CA"},
        {"name": "Mission Dolores Park", "address": "Dolores St & 19th St, San Francisco, CA"},
    ]
    optimized = optimize_stops_order(
        start_location="Fort Mason, San Francisco, CA",
        stops=input_stops,
        return_to_start=True,
    )
    # Starting from Fort Mason, Jane the Bakery (Geary Blvd) is much closer than Tartine/Dolores Park
    assert optimized[0]["name"] == "Jane the Bakery"


def test_lookup_location_info():
    from app.route_tools import lookup_location_info

    # Known food venue
    spot = lookup_location_info("Arsicault Bakery")
    assert spot["found"] is True
    assert "Arguello" in spot["address"]
    assert "08:00" in spot["open_time"]
    assert spot["type"] == "food"

    # Known park
    park = lookup_location_info("Mission Dolores Park")
    assert park["found"] is True
    assert park["type"] == "park"

    # Custom user-provided location
    custom = lookup_location_info("Custom Coffee House")
    assert custom["found"] is False
    assert "San Francisco" in custom["address"]
    assert "hours" in custom


