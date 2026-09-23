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

"""Unit tests for the Bike Planner frontend API endpoints."""

from fastapi.testclient import TestClient
from app.fast_api_app import app

client = TestClient(app)


def test_get_themes_endpoint():
    res = client.get("/api/themes?count=4&shuffle=true")
    assert res.status_code == 200
    data = res.json()
    assert "themes" in data
    assert len(data["themes"]) == 4
    for theme in data["themes"]:
        assert "title" in theme
        assert "recommended_park" in theme


def test_get_locations_for_theme_endpoint():
    payload = {
        "theme": "Chinatown Alleyways & Dumpling Roll",
        "min_food_spots": 3,
        "max_food_spots": 5,
        "min_parks": 1,
        "max_parks": 2,
    }
    res = client.post("/api/locations", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "food_spots" in data
    assert "parks" in data
    assert data["min_food_spots"] == 3
    assert data["max_food_spots"] == 5
    # Must populate at least twice the number of food spots requested (2 * 5 = 10)
    assert len(data["food_spots"]) >= 10
    assert len(data["parks"]) > 0

    # Ensure coordinates are populated for frontend map
    first_spot = data["food_spots"][0]
    assert "lat" in first_spot
    assert "lng" in first_spot
    assert first_spot["lat"] > 37.0


def test_custom_location_endpoint():
    payload = {"location_name": "Arsicault Bakery"}
    res = client.post("/api/custom-location", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["found"] is True
    assert "Arguello" in data["address"]
    assert "lat" in data
    assert "lng" in data


def test_plan_route_endpoint():
    payload = {
        "start_location": "Fort Mason, San Francisco, CA",
        "end_location": None,
        "start_time": "10:00 AM",
        "selected_stops": [
            {
                "name": "Golden Boy Pizza",
                "address": "542 Green St, San Francisco, CA",
                "type": "food",
                "hours": "Daily 11:30 AM - 10:00 PM",
                "open_time": "11:30",
                "close_time": "22:00",
            },
            {
                "name": "Washington Square Park",
                "address": "Filbert St & Stockton St, San Francisco, CA",
                "type": "park",
                "hours": "Daily 6:00 AM - 10:00 PM",
                "open_time": "06:00",
                "close_time": "22:00",
            },
        ],
        "stop_duration_minutes": 20,
        "average_transit_minutes": 15,
        "return_to_start": True,
        "optimize_order": True,
    }
    res = client.post("/api/plan-route", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "itinerary" in data
    assert len(data["itinerary"]) == 4  # Start + 2 stops + Loop Finish
    assert "google_maps_route_url" in data
    assert data["return_to_start"] is True


def test_static_planner_page():
    res = client.get("/planner")
    assert res.status_code == 200
    assert "SF Food & Bike Route Planner" in res.text
