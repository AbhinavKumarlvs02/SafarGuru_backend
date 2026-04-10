from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import multimodal_engine  # This imports your entire routing brain!

# Initialize the API
app = FastAPI(title="RADAR Mobility API", version="1.0")

# --- CORS CONFIGURATION ---
# This allows your frontend (React) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REQUEST DATA MODEL ---
# This tells FastAPI exactly what kind of JSON the frontend will send
class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    start_name: str
    end_lat: float
    end_lon: float
    end_name: str

# --- THE API ENDPOINT ---
@app.post("/api/v1/get-routes")
async def calculate_routes(request: RouteRequest):
    print(f"\n[API HIT] Incoming request for: {request.start_name} -> {request.end_name}")
    
    try:
        # Pass the frontend data directly into your McRAPTOR engine
        optimal_routes = multimodal_engine.run_multimodal_engine(
            request.start_lat, 
            request.start_lon, 
            request.start_name, 
            request.end_lat, 
            request.end_lon, 
            request.end_name
        )
        
        # Return the Pareto optimal array as clean JSON to React
        return optimal_routes
        
    except Exception as e:
        print(f"[API ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- HEALTH CHECK ---
@app.get("/")
async def root():
    return {"message": "RADAR Mobility Engine is Online."}