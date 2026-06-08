from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Smart Hybrid Fuel Consumption Calculator",
    description="Returns an HTML UI for Browsers and direct JSON for Postman using the same root URL."
)

# Hard-coded Vehicle CC and Fuel Efficiency Database (KM per Liter)
cc_fuel_matrix = {
    100: 55.0, 125: 48.0, 150: 40.0, 200: 35.0, 250: 30.0,
    660: 20.0, 800: 18.0, 1000: 16.5, 1200: 15.0, 1300: 14.0,
    1500: 12.0, 1600: 11.5, 1800: 11.0, 2000: 9.5, 2200: 9.0,
    2400: 8.5, 2500: 8.0, 2700: 7.5, 3000: 7.0
}

class CalculationRequest(BaseModel):
    cc: int
    km: float

# Helper function to perform core math
def calculate_fuel_logic(cc: int, km: float):
    if cc not in cc_fuel_matrix:
        raise HTTPException(status_code=404, detail=f"Engine CC size {cc} is not supported.")
    km_per_liter = cc_fuel_matrix[cc]
    required_liters = km / km_per_liter
    return {
        "requested_cc": cc,
        "requested_km": km,
        "km_per_liter_rate": km_per_liter,
        "required_liters": round(required_liters, 2)
    }

@app.post("/calculate-fuel")
def calculate_fuel(request: CalculationRequest):
    cc = request.cc
    km = request.km
    
    if cc not in cc_fuel_matrix:
        raise HTTPException(status_code=404, detail="Engine CC size is not supported.")
    
    km_per_liter = cc_fuel_matrix[cc]
    required_liters = km / km_per_liter
    
    return {
        "requested_cc": cc,
        "requested_km": km,
        "km_per_liter_rate": km_per_liter,
        "required_liters": round(required_liters, 2)
    }

# --- The Smart Root Endpoint ---
@app.get("/")
def home_router(request: Request, cc: Optional[int] = None, km: Optional[float] = None):
    # 1. Check if the request is coming from Postman/API (Accepts JSON)
    # Or if it's explicitly asking for a JSON structure via URL params
    accept_header = request.headers.get("accept", "")
    
    if "application/json" in accept_header or (cc is not None and km is not None and "text/html" not in accept_header):
        if cc is None or km is None:
            return {"message": "Welcome! Please provide both ?cc= and ?km= parameters to calculate fuel via JSON."}
        return calculate_fuel_logic(cc, km)

    # 2. Otherwise, treat it as a Browser request and return the HTML UI
    cc_options = ""
    for available_cc in sorted(cc_fuel_matrix.keys()):
        selected = "selected" if cc == available_cc else ""
        cc_options += f'<option value="{available_cc}" {selected}>{available_cc} CC</option>'
    
    km_value = km if km is not None else ""
    auto_calculate = "true" if (cc is not None and km is not None) else "false"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fuel Consumption Calculator</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
            body {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
            .container {{ background: #1e293b; border: 1px solid #334155; padding: 40px; border-radius: 20px; box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.3); width: 100%; max-width: 480px; }}
            h2 {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; text-align: center; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            p.subtitle {{ color: #94a3b8; font-size: 14px; text-align: center; margin-bottom: 30px; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; font-size: 14px; font-weight: 500; margin-bottom: 8px; color: #cbd5e1; }}
            select, input {{ width: 100%; padding: 12px 16px; background: #0f172a; border: 1px solid #334155; border-radius: 10px; color: #f8fafc; font-size: 15px; transition: all 0.3s ease; outline: none; }}
            select:focus, input:focus {{ border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2); }}
            button {{ width: 100%; padding: 14px; background: #38bdf8; border: none; border-radius: 10px; color: #0f172a; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; margin-top: 10px; }}
            button:hover {{ background: #0ea5e9; transform: translateY(-1px); }}
            .result-card {{ display: none; margin-top: 30px; padding: 20px; background: #0f172a; border: 1px solid #334155; border-radius: 12px; }}
            .result-title {{ font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; font-weight: 600; }}
            .result-value {{ font-size: 32px; font-weight: 700; color: #4ade80; display: flex; align-items: baseline; gap: 4px; }}
            .result-value span {{ font-size: 16px; color: #94a3b8; font-weight: 400; }}
            .info-row {{ display: flex; justify-content: space-between; margin-top: 15px; padding-top: 15px; border-top: 1px solid #334155; font-size: 14px; color: #cbd5e1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Fuel Calculator</h2>
            <p class="subtitle">Calculate required fuel liters based on engine CC</p>
            
            <div class="form-group">
                <label for="cc">Select Vehicle CC</label>
                <select id="cc">{cc_options}</select>
            </div>
            
            <div class="form-group">
                <label for="km">Distance to Travel (KM)</label>
                <input type="number" id="km" value="{km_value}" placeholder="e.g. 150" min="0" step="any">
            </div>
            
            <button onclick="calculateFuel()">Calculate Liters</button>
            
            <div class="result-card" id="resultCard">
                <div class="result-title">Required Fuel</div>
                <div class="result-value" id="litersResult">0.00 <span>Liters</span></div>
                <div class="info-row">
                    <span>Efficiency Rate:</span>
                    <span id="rateResult">0 KM/L</span>
                </div>
            </div>
        </div>

        <script>
            async function calculateFuel() {{
                const cc = document.getElementById('cc').value;
                const km = document.getElementById('km').value;
                const resultCard = document.getElementById('resultCard');
                
                if(!km || km <= 0) {{
                    alert('Please enter a valid distance.');
                    return;
                }}
                
                try {{
                    // Fetch directly from the root with parameters to avoid multiple paths
                    const response = await fetch(`/?cc=${{cc}}&km=${{km}}`, {{
                        headers: {{ 'Accept': 'application/json' }}
                    }});
                    const data = await response.json();
                    
                    if(response.ok) {{
                        document.getElementById('litersResult').innerHTML = `${{data.required_liters}} <span>Liters</span>`;
                        document.getElementById('rateResult').innerText = `${{data.km_per_liter_rate}} KM/L`;
                        resultCard.style.display = 'block';
                    }} else {{
                        alert(data.detail || 'Something went wrong');
                    }}
                }} catch (error) {{
                    alert('Error connecting to the server');
                }}
            }}

            if ({auto_calculate}) {{
                window.addEventListener('DOMContentLoaded', calculateFuel);
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

