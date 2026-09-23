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

"""FastAPI router providing REST API endpoints for the bike route planner frontend."""

from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.route_tools import (
    SF_PARKS,
    calculate_bike_route_schedule,
    find_food_spots,
    lookup_location_info,
    suggest_food_themes,
    _get_location_coords,
)

router = APIRouter(prefix="/api", tags=["planner"])


class ThemeQueryRequest(BaseModel):
    query_context: str = ""
    count: int = 4
    shuffle: bool = True


class LocationQueryRequest(BaseModel):
    theme: str
    neighborhood: str | None = None
    min_food_spots: int = Field(default=2, ge=1, le=10)
    max_food_spots: int = Field(default=4, ge=1, le=10)
    min_parks: int = Field(default=1, ge=0, le=5)
    max_parks: int = Field(default=2, ge=0, le=5)


class CustomLocationRequest(BaseModel):
    location_name: str


class PlanRouteRequest(BaseModel):
    start_location: str = "Fort Mason, San Francisco, CA"
    end_location: str | None = None
    start_time: str = "10:00 AM"
    selected_stops: list[dict[str, Any]] = []
    stop_duration_minutes: int = 20
    average_transit_minutes: int = 15
    return_to_start: bool = True
    optimize_order: bool = True


@router.get("/themes")
def get_themes(count: int = 4, shuffle: bool = True) -> dict[str, Any]:
    """Returns suggested food themes with shuffle support."""
    return suggest_food_themes(count=count, shuffle=shuffle)


@router.post("/themes")
def post_themes(payload: ThemeQueryRequest) -> dict[str, Any]:
    """Returns food themes matching context or refreshed themes."""
    return suggest_food_themes(
        query_context=payload.query_context,
        count=payload.count,
        shuffle=payload.shuffle,
    )


@router.post("/locations")
def get_locations_for_theme(payload: LocationQueryRequest) -> dict[str, Any]:
    """Returns candidate food spots and curated parks with coordinates for the map.

    Populates at least twice the maximum number of food spots requested by the user.
    """
    candidate_limit = max(payload.max_food_spots * 2, 12)
    spots_data = find_food_spots(theme=payload.theme, neighborhood=payload.neighborhood, limit=candidate_limit)
    candidate_spots = spots_data.get("candidate_spots", [])

    # Enrich spots with coordinates and default selection metadata
    enriched_spots = []
    for spot in candidate_spots:
        coords = _get_location_coords(spot["name"] + " " + spot["address"])
        enriched_spots.append({
            "name": spot["name"],
            "address": spot["address"],
            "neighborhood": spot.get("neighborhood", "San Francisco"),
            "hours": spot.get("hours", "Check hours"),
            "open_time": spot.get("open_time", "09:00"),
            "close_time": spot.get("close_time", "18:00"),
            "specialty": spot.get("specialty", ""),
            "theme": spot.get("theme", payload.theme),
            "type": "food",
            "lat": coords[0],
            "lng": coords[1],
        })

    # Curate parks: prioritize parks that work well with the theme/neighborhood and scale suggestions to at least 2x max_parks
    park_candidate_limit = max(payload.max_parks * 2, 6)
    
    # Check if theme recommends a specific park or neighborhood
    recommended_parks = []
    other_parks = []
    
    theme_lower = payload.theme.lower()
    for park in SF_PARKS:
        p_name = park["name"].lower()
        p_neigh = park["neighborhood"].lower()
        
        # Match theme affinities
        is_affinity = False
        if ("chinatown" in theme_lower or "slice" in theme_lower or "north beach" in theme_lower) and "washington square" in p_name:
            is_affinity = True
        elif ("burrito" in theme_lower or "mission" in theme_lower or "latin" in theme_lower) and ("mission dolores" in p_name or "bernal" in p_name):
            is_affinity = True
        elif ("cookie" in theme_lower or "baker" in theme_lower or "roast" in theme_lower or "glazed" in theme_lower) and ("alamo square" in p_name or "duboce" in p_name or "panhandle" in p_name):
            is_affinity = True
        elif ("waterfront" in theme_lower or "sourdough" in theme_lower or "chowder" in theme_lower or "presidio" in theme_lower) and ("marina green" in p_name or "tunnel tops" in p_name or "crissy field" in p_name):
            is_affinity = True
            
        if is_affinity:
            recommended_parks.append(park)
        else:
            other_parks.append(park)

    selected_parks_pool = (recommended_parks + other_parks)[:park_candidate_limit]

    parks_list = []
    for park in selected_parks_pool:
        coords = _get_location_coords(park["name"] + " " + park["address"])
        parks_list.append({
            "name": park["name"],
            "address": park["address"],
            "neighborhood": park.get("neighborhood", "San Francisco"),
            "hours": park.get("hours", "Daily 6:00 AM - 10:00 PM"),
            "open_time": park.get("open_time", "06:00"),
            "close_time": park.get("close_time", "22:00"),
            "specialty": park.get("vibe", "Scenic picnic lawn with views"),
            "amenities": park.get("amenities", ""),
            "type": "park",
            "lat": coords[0],
            "lng": coords[1],
        })

    return {
        "theme": payload.theme,
        "min_food_spots": payload.min_food_spots,
        "max_food_spots": payload.max_food_spots,
        "min_parks": payload.min_parks,
        "max_parks": payload.max_parks,
        "food_spots": enriched_spots,
        "parks": parks_list,
    }



@router.post("/custom-location")
def add_custom_location(payload: CustomLocationRequest) -> dict[str, Any]:
    """Looks up information and coordinates for a user-specified custom location."""
    info = lookup_location_info(payload.location_name)
    coords = _get_location_coords(info["name"] + " " + info["address"])
    info["lat"] = coords[0]
    info["lng"] = coords[1]
    return info


@router.post("/plan-route")
def plan_route(payload: PlanRouteRequest) -> dict[str, Any]:
    """Calculates an optimized bike route schedule, store verification, and closed-loop navigation link."""
    return calculate_bike_route_schedule(
        start_location=payload.start_location,
        start_time=payload.start_time,
        stops=payload.selected_stops,
        stop_duration_minutes=payload.stop_duration_minutes,
        average_transit_minutes=payload.average_transit_minutes,
        return_to_start=payload.return_to_start,
        end_location=payload.end_location,
        optimize_order=payload.optimize_order,
    )
