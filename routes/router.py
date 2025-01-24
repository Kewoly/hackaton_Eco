from typing import List, Union, Dict, Optional
from fastapi import APIRouter, Request, HTTPException, status
from geopy.geocoders import Nominatim
from pydantic import BaseModel
import math
import uuid
from bson.objectid import ObjectId
import joblib
import pandas as pd

router = APIRouter()

@router.get("/ping")
async def ping(request: Request):
    """ Check if the API is running """
    return {"ping": "pong"}

async def get_coordinates(address: str) -> Dict[str, float]:
    """Convert address to coordinates"""
    geolocator = Nominatim(user_agent="carbon_footprint_calculator")
    location = geolocator.geocode(address)
    if location:
        return {"lat": location.latitude, "lng": location.longitude}
    raise ValueError(f"Could not geocode address: {address}")

async def predict_car_emissions(model, cylinders, consumption):
    """
    Predict car emissions using named features.
    
    Parameters:
    -----------
    model : trained model object
        The pre-trained model for emissions prediction
    cylinders : int
        Number of cylinders in the car
    consumption : float
        Fuel consumption in L/100 km
        
    Returns:
    --------
    float
        Predicted emission factor
    """
    # Create feature names
    feature_names = ['Cylinders', 'Fuel Consumption Comb (L/100 km)']
    
    # Create input features as a dictionary
    features = {
        'Cylinders': cylinders,
        'Fuel Consumption Comb (L/100 km)': consumption
    }
    
    # Convert to DataFrame to ensure feature order
    X = pd.DataFrame([features])[feature_names]
    
    # Make prediction
    car_emission_factor = model.predict(X)[0]
    
    return car_emission_factor

class Coordinate(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    
class CarParameters(BaseModel):
    cylinders: int # Number of cylinders
    consumption: float # L/100km

class ItineraryRequest(BaseModel):
    itinerary: List[Coordinate]
    car_params: CarParameters = None

@router.post("/footprint", response_description="Get Carbon Footprint of an Itinerary", status_code=status.HTTP_201_CREATED)
async def footprint(request: Request, body: ItineraryRequest):
    """Calculate the CO2 footprint of an itinerary"""
    
    footprints = {
        "carFootprint": 0.0,
        "busFootprint": 0.0,
        "truckFootprint": 0.0,
        "trainFootprint": 0.0,
        "planeFootprint": 0.0,
        "walkingFootprint": 0.0,
        "bikingFootprint": 0.0
    }

    # Convert addresses to coordinates if needed
    coordinates = []
    for point in body.itinerary:
        if point.address and not (point.lat and point.lng):
            try:
                coords = await get_coordinates(point.address)
                coordinates.append(coords)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        elif point.lat and point.lng:
            coordinates.append({"lat": point.lat, "lng": point.lng})
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each point must have either coordinates (lat/lng) or an address"
            )

    # Calculate total distance from points
    total_distance = 0
    for i in range(len(coordinates)-1):
        start = coordinates[i]
        end = coordinates[i+1]
        
        # Calculate distance between points using Haversine formula
        R = 6371  # Earth's radius in km
        lat1, lon1 = start['lat'], start['lng']
        lat2, lon2 = end['lat'], end['lng']
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        total_distance += distance

    # Calculate footprints based on distance and emission factors
    if body.car_params:
        # Prepare features for the model
        features = {
            "cylinders": body.car_params.cylinders,
            "consumption": body.car_params.consumption,
        }
        
        model = joblib.load("models/model.pkl")
        
        # Predict car emissions
        car_emission_factor = await predict_car_emissions(model, **features)
        
        footprints["carFootprint"] = total_distance * car_emission_factor
    else:
        footprints["carFootprint"] = total_distance * 120  # Default 120g CO2/km



    # Calculate footprints based on distance and emission factors
    footprints["busFootprint"] = total_distance * 80   # 80g CO2/km
    footprints["truckFootprint"] = total_distance * 160  # 160g CO2/km
    footprints["trainFootprint"] = total_distance * 30   # 30g CO2/km
    footprints["planeFootprint"] = total_distance * 150  # 150g CO2/km
    footprints["walkingFootprint"] = total_distance * 10  # 10g CO2/km
    footprints["bikingFootprint"] = total_distance * 10   # 10g CO2/km

    return footprints