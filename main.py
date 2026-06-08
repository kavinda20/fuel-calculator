from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI App
app = FastAPI(
    title="Comprehensive Fuel Consumption Calculator API",
    description="API with hard-coded fuel efficiency rates for almost all common vehicle CC sizes in Sri Lanka."
)

# 1. Hard-coded Data Store for almost all common vehicles
# Key = CC size, Value = Average Kilometers per Liter (KM/L)
cc_fuel_matrix = {
    # --- Bikes & Three-Wheelers ---
    100: 55.0,   # 100cc Bikes (CT100, etc.)
    125: 48.0,   # 125cc Bikes (Discover, Grazia)
    150: 40.0,   # 150cc Bikes (FZ, Pulsar)
    200: 35.0,   # 200cc Bikes (Pulsar 200NS)
    250: 30.0,   # 250cc & 4-stroke Three-Wheelers / Bikes
    
    # --- Small Cars & Hatchbacks ---
    660: 20.0,   # 660cc Japanese Turbo/Non-Turbo Cars (Alto, WagonR)
    800: 18.0,   # 800cc Cars (Maruti 800, Indian Alto)
    1000: 16.5,  # 1000cc Cars (Vitz, Pixis, Kwid, Celerio)
    
    # --- Sedans, SUVs & Vans ---
    1200: 15.0,  # 1200cc Cars (Swift, Aqua - Hybrid average)
    1300: 14.0,  # 1300cc Cars (Yaris, Solio)
    1500: 12.0,  # 1500cc Standard Cars/Vans (Axio, Grace, Vezel, Allion, Premio)
    1600: 11.5,  # 1600cc Cars (Civic, Bluebird)
    1800: 11.0,  # 1800cc Cars/Prius (Prius Hybrid can be higher, but keeping non-hybrid/average baseline)
    2000: 9.5,   # 2000cc Large Sedans / Crossovers (X-Trail, CRV, CHR)
    2200: 9.0,   # 2200cc Turbo Diesel (Montero Sport / Caravan)
    2400: 8.5,   # 2400cc Large SUVs (Prado, Outlander)
    2500: 8.0,   # 2500cc Large Vans / Luxury Sedans (KDH, Camry)
    2700: 7.5,   # 2700cc Petrol Luxury SUVs (Prado Petrol)
    3000: 7.0    # 3000cc V6 or Turbo Diesel Luxury Vehicles (Montero V6 / Land Cruiser)
}

# Request schema for incoming JSON data
class CalculationRequest(BaseModel):
    cc: int
    km: float

# Home Endpoint
@app.get("/")
def home():
    return {
        "status": "Healthy",
        "message": "Comprehensive Fuel Calculator API is running successfully!",
        "total_supported_cc_sizes": len(cc_fuel_matrix)
    }

# Endpoint to check what CCs are hard-coded in the system
@app.get("/supported-cc")
def get_supported_cc():
    return {
        "description": "List of all hard-coded CC sizes and their assumed KM per Liter rate.",
        "rates": cc_fuel_matrix
    }

# Main Fuel Calculation Endpoint
@app.post("/calculate-fuel")
def calculate_fuel(request: CalculationRequest):
    cc = request.cc
    km = request.km
    
    # Check if the exact CC exists
    if cc not in cc_fuel_matrix:
        # If exact CC is not found, we can suggest the closest available CCs
        available_ccs = sorted(list(cc_fuel_matrix.keys()))
        raise HTTPException(
            status_code=404, 
            detail=f"CC {cc} is not hard-coded in the system. Please use a standard common CC like: {available_ccs}"
        )
    
    km_per_liter = cc_fuel_matrix[cc]
    required_liters = km / km_per_liter
    
    return {
        "requested_cc": cc,
        "requested_km": km,
        "km_per_liter_rate": km_per_liter,
        "required_liters": round(required_liters, 2)
    }
