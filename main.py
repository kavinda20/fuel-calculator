from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize the FastAPI application
app = FastAPI(
    title="Fuel Consumption Calculator API",
    description="An API that stores CC-to-fuel efficiency rates and calculates required liters based on distance (KM)."
)

# 1. System Data Store (In-Memory Dictionary)
# Key = CC Size, Value = Kilometers per Liter (KM/L)
cc_fuel_matrix = {
    1000: 18.0,  # 1000cc -> 1 Liter = 18km
    1200: 15.0,  # 1200cc -> 1 Liter = 15km
    1500: 12.0,  # 1500cc -> 1 Liter = 12km
    2000: 9.0    # 2000cc -> 1 Liter = 9km
}

# Define the expected JSON structure for incoming requests (Request Body Schema)
class CalculationRequest(BaseModel):
    cc: int
    km: float

# Home Endpoint (To verify if the API is online and working)
@app.get("/")
def home():
    return {
        "status": "Healthy",
        "message": "Fuel Calculator API is running successfully!"
    }

# Main POST Endpoint to calculate fuel consumption
@app.post("/calculate-fuel")
def calculate_fuel(request: CalculationRequest):
    cc = request.cc
    km = request.km
    
    # Check if the requested CC exists in our system matrix
    if cc not in cc_fuel_matrix:
        raise HTTPException(
            status_code=404, 
            detail=f"Sorry, CC {cc} is not found in our system. Available CCs are: {list(cc_fuel_matrix.keys())}"
        )
    
    # Retrieve the fuel efficiency rate for the specific CC
    km_per_liter = cc_fuel_matrix[cc]
    
    # Calculate the total liters required (Liters = KM / KM per Liter)
    required_liters = km / km_per_liter
    
    # Return the structured JSON response, rounding liters to 2 decimal places
    return {
        "requested_cc": cc,
        "requested_km": km,
        "km_per_liter_rate": km_per_liter,
        "required_liters": round(required_liters, 2)
    }