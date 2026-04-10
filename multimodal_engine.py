# import json
# import math
# import sys
# import os
# import heapq

# # --- WINDOWS SAFETY ---
# if sys.platform.startswith('win'):
#     sys.stdout.reconfigure(encoding='utf-8')

# script_dir = os.path.dirname(os.path.abspath(__file__))
# json_file_path = os.path.join(script_dir, 'delhi_metro_graph_real.json')

# # Load the Metro Graph
# with open(json_file_path, 'r', encoding='utf-8') as f:
#     metro_graph = json.load(f)

# # ==========================================
# # 1. THE AI CAB PRICING ENGINE (ST-GCN WRAPPER)
# # ==========================================
# class AICabEngine:
#     def __init__(self):
#         # In production, import torch and load your model here:
#         # self.model = STGCN()
#         # self.model.load_state_dict(torch.load('delhi_final_stgcn.pth'))
#         # self.model.eval()
#         self.base_fare = 50.0  # Rs
#         self.rate_per_km = 15.0 # Rs/km

#     def _encode_features(self, time_of_day, traffic, road_type):
#         """Converts strings to your exact categorical floats."""
#         encodings = {
#             "time": {"Night": 0.0, "Morning Peak": 1.0, "Afternoon": 2.0, "Evening Peak": 3.0},
#             "traffic": {"Low": 0.0, "Medium": 0.3, "High": 0.7, "Very High": 1.1},
#             "road": {"Highway": 0.0, "Main Road": 0.2, "Inner Road": 0.5}
#         }
#         return (
#             encodings["time"].get(time_of_day, 2.0),
#             encodings["traffic"].get(traffic, 0.3),
#             encodings["road"].get(road_type, 0.2)
#         )

#     def predict_surge_delta(self, lat, lon, time_of_day, traffic, road_type):
#         """
#         Prepares the [1, 3, 500, 3] tensor and runs inference.
#         """
#         t_val, tr_val, r_val = self._encode_features(time_of_day, traffic, road_type)
        
#         # --- PYTORCH INTEGRATION ZONE ---
#         # 1. Use h3-pandas to convert lat/lon to node_index (0-499)
#         # 2. Build the Tensor: shape [Batch=1, TimeSteps=3, Nodes=500, Features=3]
#         # tensor_input = torch.zeros((1, 3, 500, 3))
#         # tensor_input[0, :, node_index, 0] = t_val
#         # tensor_input[0, :, node_index, 1] = tr_val
#         # tensor_input[0, :, node_index, 2] = r_val
#         # surge_delta = self.model(tensor_input).item()
        
#         # MOCK PREDICTION FOR ROUTING TEST:
#         if traffic == "High": return 0.45  # 45% surge
#         if traffic == "Very High": return 0.80 # 80% surge
#         return 0.10 # 10% standard surge

#     def calculate_fare(self, distance_km, surge_delta):
#         """Implements your exact pricing formula."""
#         return (self.base_fare + (distance_km * self.rate_per_km)) * (1.0 + surge_delta)

#     def estimate_cab_time(self, distance_km, traffic):
#         speed_kmh = {"Low": 40, "Medium": 25, "High": 15, "Very High": 10}.get(traffic, 25)
#         return int((distance_km / speed_kmh) * 60) # minutes

# # ==========================================
# # 2. GEOGRAPHIC HELPERS (HAVERSINE)
# # ==========================================
# def haversine(lat1, lon1, lat2, lon2):
#     """Calculates straight-line distance between two GPS coordinates in km."""
#     R = 6371.0 # Earth radius
#     dlat = math.radians(lat2 - lat1)
#     dlon = math.radians(lon2 - lon1)
#     a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# # Mock station coordinates (You will need to link this to your GTFS/CSV lat-longs)
# STATION_COORDS = {
#     "SECTOR_51_AQUA_LINE": (28.5847, 77.3653),
#     "BOTANICAL_GARDEN_BLUE_LINE": (28.5640, 77.3256),
#     "RAJIV_CHOWK_YELLOW_LINE": (28.6328, 77.2197),
#     "HAUZ_KHAS_YELLOW_LINE": (28.5432, 77.2066)
# }

# def get_nearest_stations(lat, lon, k=2):
#     """Finds the 'k' nearest metro stations to a GPS pin."""
#     distances = []
#     for stn_id, coords in STATION_COORDS.items():
#         if stn_id in metro_graph:
#             dist = haversine(lat, lon, coords[0], coords[1])
#             distances.append((dist, stn_id))
#     distances.sort()
#     return distances[:k]

# # ==========================================
# # 3. METRO ROUTING ENGINE (Imported from previous step)
# # ==========================================
# # (Assuming find_fastest_route and calculate_accurate_fare exist here as we wrote them)
# def mock_metro_route(start_id, end_id):
#     """Placeholder for the Dijsktra algorithm we built earlier."""
#     if start_id == end_id: return 0, 0 # Time(mins), Fare(Rs)
#     return 45, 50 # Example: 45 mins, Rs 50 

# # ==========================================
# # 4. THE McRAPTOR MASTER ALGORITHM
# # ==========================================
# def calculate_multimodal_options(start_lat, start_lon, end_lat, end_lon, context):
#     cab_engine = AICabEngine()
#     options = []

#     # --- OPTION 1: DIRECT CAB RIDE ---
#     direct_dist = haversine(start_lat, start_lon, end_lat, end_lon) * 1.3 # 1.3 multiplier for road layout
#     surge = cab_engine.predict_surge_delta(start_lat, start_lon, context['time'], context['traffic'], context['road'])
#     direct_cost = cab_engine.calculate_fare(direct_dist, surge)
#     direct_time = cab_engine.estimate_cab_time(direct_dist, context['traffic'])
    
#     options.append({
#         "type": "Direct Cab",
#         "time_mins": direct_time,
#         "cost_rs": round(direct_cost, 2),
#         "details": f"Cab entire way ({direct_dist:.1f} km)"
#     })

#     # --- OPTION 2: HYBRID (CAB -> METRO -> CAB) ---
#     start_stations = get_nearest_stations(start_lat, start_lon)
#     end_stations = get_nearest_stations(end_lat, end_lon)

#     for dist_to_start, start_stn in start_stations:
#         for dist_to_end, end_stn in end_stations:
            
#             # 1. First Mile Cab
#             surge1 = cab_engine.predict_surge_delta(start_lat, start_lon, context['time'], context['traffic'], "Inner Road")
#             cost1 = cab_engine.calculate_fare(dist_to_start * 1.3, surge1)
#             time1 = cab_engine.estimate_cab_time(dist_to_start * 1.3, context['traffic'])

#             # 2. Metro Journey (Using your calibrated JSON graph)
#             metro_time, metro_fare = mock_metro_route(start_stn, end_stn)

#             # 3. Last Mile Cab
#             surge2 = cab_engine.predict_surge_delta(end_lat, end_lon, context['time'], context['traffic'], "Inner Road")
#             cost2 = cab_engine.calculate_fare(dist_to_end * 1.3, surge2)
#             time2 = cab_engine.estimate_cab_time(dist_to_end * 1.3, context['traffic'])

#             total_time = time1 + metro_time + time2
#             total_cost = cost1 + metro_fare + cost2

#             options.append({
#                 "type": "Hybrid (Cab + Metro)",
#                 "time_mins": total_time,
#                 "cost_rs": round(total_cost, 2),
#                 "details": f"Cab to {metro_graph[start_stn]['name']} -> Metro to {metro_graph[end_stn]['name']} -> Cab to destination."
#             })

#     # --- PARETO FILTER ---
#     # We only keep routes that are not "dominated" by another route.
#     # Route A dominates Route B if A is BOTH faster AND cheaper than B.
#     pareto_optimal = []
#     for opt_a in options:
#         is_dominated = False
#         for opt_b in options:
#             if opt_a == opt_b: continue
#             if opt_b['time_mins'] <= opt_a['time_mins'] and opt_b['cost_rs'] < opt_a['cost_rs']:
#                 is_dominated = True
#                 break
#             if opt_b['time_mins'] < opt_a['time_mins'] and opt_b['cost_rs'] <= opt_a['cost_rs']:
#                 is_dominated = True
#                 break
#         if not is_dominated:
#             pareto_optimal.append(opt_a)

#     return pareto_optimal

# # ==========================================
# # 5. EXECUTION & TEST
# # ==========================================
# if __name__ == "__main__":
#     # Simulate a user requesting a ride from an apartment in Greater Noida to Hauz Khas during Evening Peak
#     USER_START = (28.4500, 77.5840) # Bennett
#     USER_END = (28.5880, 77.2530)   # NZM
    
#     CONTEXT = {
#         "time": "Evening Peak",
#         "traffic": "High",
#         "road": "Main Road"
#     }

#     print("\n[AI CAB ENGINE] Fetching localized surge multipliers...")
#     print("[MULTI-MODAL ENGINE] Calculating Pareto-optimal routes...\n")
    
#     results = calculate_multimodal_options(USER_START[0], USER_START[1], USER_END[0], USER_END[1], CONTEXT)
    
#     print("🎯 RECOMMENDED ROUTES (PARETO FRONTIER):")
#     for idx, r in enumerate(results, 1):
#         print(f"\n{idx}. {r['type']}")
#         print(f"   ⏱️ Time: {r['time_mins']} mins")
#         print(f"   💸 Cost: Rs. {r['cost_rs']}")
#         print(f"   🗺️ Path: {r['details']}")
























# import json
# import math
# import heapq
# import sys
# import os
# import googlemaps
# from datetime import datetime

# # --- WINDOWS SAFETY ---
# if sys.platform.startswith('win'):
#     sys.stdout.reconfigure(encoding='utf-8')

# script_dir = os.path.dirname(os.path.abspath(__file__))
# json_graph_path = os.path.join(script_dir, 'delhi_metro_graph_real.json')

# # ==========================================
# # 1. LOAD THE UNIFIED METRO GRAPH
# # ==========================================
# try:
#     with open(json_graph_path, 'r', encoding='utf-8') as f:
#         metro_graph = json.load(f)
# except FileNotFoundError:
#     print(f"[ERROR] Graph missing: '{json_graph_path}'")
#     sys.exit()

# # ==========================================
# # 2. THE AI CAB & WALKING ENGINE
# # ==========================================
# class AICabEngine:
#     def __init__(self):
#         self.base_fare = 50.0  
#         self.rate_per_km = 15.0 
        
#         # --- GOOGLE MAPS API INJECTION ---
#         # Replace this string with your actual API key when ready
#         self.gmaps = googlemaps.Client(key='YOUR_GOOGLE_MAPS_API_KEY')

#     def predict_surge_delta(self, lat, lon, time_of_day, traffic, road_type):
#         """Mocks the ST-GCN PyTorch Inference"""
#         if traffic == "High": return 0.45 
#         if traffic == "Very High": return 0.80
#         if traffic == "Medium": return 0.20
#         return 0.10 

#     def calculate_fare_breakdown(self, distance_km, surge_delta):
#         distance_fare = distance_km * self.rate_per_km
#         subtotal = self.base_fare + distance_fare
#         surge_amount = subtotal * surge_delta
#         return {
#             "base": self.base_fare, 
#             "distance_fare": distance_fare, 
#             "surge_amount": surge_amount, 
#             "total": subtotal + surge_amount
#         }

#     def get_real_world_routing(self, origin_coords, dest_coords):
#         """Calls Google Maps for live traffic time and real road distance."""
#         try:
#             # Note: We bypass the API call if the key is obviously unconfigured
#             if self.gmaps.key == 'YOUR_GOOGLE_MAPS_API_KEY':
#                 return None, None
                
#             matrix = self.gmaps.distance_matrix(
#                 origins=origin_coords,
#                 destinations=dest_coords,
#                 mode="driving",
#                 departure_time=datetime.now() # Forces live traffic
#             )
#             element = matrix['rows'][0]['elements'][0]
#             if element['status'] == 'OK':
#                 real_dist_km = element['distance']['value'] / 1000.0
#                 if 'duration_in_traffic' in element:
#                     real_time_mins = element['duration_in_traffic']['value'] // 60
#                 else:
#                     real_time_mins = element['duration']['value'] // 60
#                 return real_dist_km, real_time_mins
#         except Exception as e:
#             print(f"[API WARNING] Could not reach Google Maps: {e}")
        
#         return None, None

# def haversine(lat1, lon1, lat2, lon2):
#     """Calculates straight-line GPS distance in km."""
#     R = 6371.0 
#     a = math.sin(math.radians(lat2 - lat1) / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon1) / 2)**2
#     return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

# def get_leg_options(start_coords, end_coords, context, cab_engine):
#     """
#     THE GATEKEEPER: 
#     If local math says the walk is <= 20 mins, forces Walk and BLOCKS the API call.
#     Otherwise, fires the Google Maps API.
#     """
#     options = []
    
#     # 1. Local Gatekeeper Math (Free, 0 Latency)
#     haversine_dist_km = haversine(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
#     estimated_street_dist = haversine_dist_km * 1.3
#     walk_time_mins = int((estimated_street_dist / 5.0) * 60) # 5 km/h walking speed
    
#     if walk_time_mins <= 20:
#         # FORCE WALK: API IS BLOCKED
#         options.append({
#             "mode": "Walk", 
#             "time": walk_time_mins, 
#             "cost": 0.0,
#             "breakdown": {"base": 0, "distance_fare": 0, "surge_amount": 0, "total": 0}
#         })
#     else:
#         # FORCE CAB: GOOGLE MAPS API IS CALLED
#         real_dist, real_time = cab_engine.get_real_world_routing(start_coords, end_coords)
        
#         # Fallback just in case your API key is invalid or missing
#         if real_dist is None:
#             real_dist = estimated_street_dist
#             speed_kmh = {"Low": 40, "Medium": 25, "High": 15, "Very High": 10}.get(context['traffic'], 25)
#             real_time = int((real_dist / speed_kmh) * 60) 

#         surge = cab_engine.predict_surge_delta(start_coords[0], start_coords[1], context['time'], context['traffic'], "Inner Road")
#         cab_breakdown = cab_engine.calculate_fare_breakdown(real_dist, surge)
        
#         options.append({
#             "mode": "Cab", 
#             "time": real_time, 
#             "cost": cab_breakdown['total'],
#             "breakdown": cab_breakdown,
#             "real_dist_km": real_dist
#         })
        
#     return options

# # ==========================================
# # 3. METRO ROUTING & FARE ENGINE
# # ==========================================
# AVG_SPEED_KMPH = 45.0       
# DWELL_TIME_SEC = 25         
# INITIAL_WAIT_SEC = 300      

# def get_slab_fare(d):
#     if d == 0: return 0
#     if d <= 2.0: return 10
#     elif d <= 5.0: return 20
#     elif d <= 12.0: return 30
#     elif d <= 21.0: return 40
#     elif d <= 32.0: return 50
#     else: return 60

# def calculate_accurate_fare(route):
#     """Splits journey by agency (DMRC vs NMRC)"""
#     dmrc_dist, aqua_dist = 0.0, 0.0
#     for i in range(len(route) - 1):
#         curr_node, next_node = route[i], route[i+1]
#         edge_dist = next(e["distance_km"] for e in metro_graph[curr_node]["connections"] if e["to"] == next_node)
        
#         line_name = metro_graph[next_node]['line'].upper()
#         if "AQUA" in line_name: aqua_dist += edge_dist
#         else: dmrc_dist += edge_dist

#     dmrc_fare = get_slab_fare(dmrc_dist)
#     aqua_fare = get_slab_fare(aqua_dist)
#     return dmrc_fare + aqua_fare, dmrc_fare, aqua_fare

# def find_fastest_route(start_id, end_id):
#     if start_id not in metro_graph or end_id not in metro_graph: return None, 0, 0

#     pq = [(INITIAL_WAIT_SEC, start_id, 0.0)]
#     min_times = {start_id: INITIAL_WAIT_SEC}
#     came_from = {}

#     while pq:
#         current_time, current_node, current_dist = heapq.heappop(pq)
#         if current_node == end_id:
#             path = []
#             while current_node in came_from:
#                 path.append(current_node)
#                 current_node = came_from[current_node]
#             path.append(start_id)
#             return path[::-1], current_time, current_dist

#         for edge in metro_graph[current_node]["connections"]:
#             neighbor = edge["to"]
#             edge_time_sec = int((edge["distance_km"] / AVG_SPEED_KMPH) * 3600) + DWELL_TIME_SEC if edge["type"] == "rail" else edge["time_sec"]
            
#             new_time = current_time + edge_time_sec
#             new_dist = current_dist + edge["distance_km"]

#             if neighbor not in min_times or new_time < min_times[neighbor]:
#                 min_times[neighbor] = new_time
#                 came_from[neighbor] = current_node
#                 heapq.heappush(pq, (new_time, neighbor, new_dist))
#     return None, 0, 0

# def get_nearest_stations(lat, lon, k=2):
#     """Finds the 'k' closest Metro stations dynamically."""
#     distances = []
#     for stn_id, data in metro_graph.items():
#         if 'lat' in data and 'lon' in data:
#             dist = haversine(lat, lon, data['lat'], data['lon'])
#             distances.append((dist, stn_id))
#     return sorted(distances)[:k]

# # ==========================================
# # 4. MULTI-MODAL McRAPTOR LOGIC
# # ==========================================
# def run_multimodal_engine(start_lat, start_lon, end_lat, end_lon, context):
#     cab_engine = AICabEngine()
#     options = []
    
#     start_coords = (start_lat, start_lon)
#     end_coords = (end_lat, end_lon)

#     # --- 1. DIRECT ROUTE (Door-to-Door) ---
#     direct_leg = get_leg_options(start_coords, end_coords, context, cab_engine)[0]
#     dist_label = f"({direct_leg.get('real_dist_km', 0):.1f} km)" if direct_leg['mode'] == 'Cab' else ""
    
#     options.append({
#         "type": f"Direct {direct_leg['mode']}", 
#         "time": direct_leg['time'], 
#         "cost": direct_leg['cost'], 
#         "desc": f"{direct_leg['mode']} entire way {dist_label}", 
#         "cab_breakdown": direct_leg['breakdown'],
#         "time_breakdown": {"leg1": direct_leg['time'], "metro": 0, "leg2": 0},
#         "leg1_mode": direct_leg['mode'], "leg2_mode": None
#     })

#     # --- 2. HYBRID ROUTES (Leg 1 -> Metro -> Leg 2) ---
#     start_stns = get_nearest_stations(start_lat, start_lon, k=2)
#     end_stns = get_nearest_stations(end_lat, end_lon, k=2)

#     for dist_to_start, start_stn in start_stns:
#         for dist_to_end, end_stn in end_stns:
            
#             start_stn_coords = (metro_graph[start_stn]['lat'], metro_graph[start_stn]['lon'])
#             end_stn_coords = (metro_graph[end_stn]['lat'], metro_graph[end_stn]['lon'])

#             # Pass through the Gatekeeper to get Walk or Cab
#             fm = get_leg_options(start_coords, start_stn_coords, context, cab_engine)[0]
#             lm = get_leg_options(end_stn_coords, end_coords, context, cab_engine)[0]

#             # Calculate Metro middle leg
#             route, metro_time_sec, metro_dist = find_fastest_route(start_stn, end_stn)
#             if not route: continue
#             metro_time = metro_time_sec // 60
#             metro_total_fare, dmrc_f, aqua_f = calculate_accurate_fare(route)

#             # Combine receipts
#             combined_cab_breakdown = {
#                 "base": fm['breakdown']['base'] + lm['breakdown']['base'],
#                 "distance_fare": fm['breakdown']['distance_fare'] + lm['breakdown']['distance_fare'],
#                 "surge_amount": fm['breakdown']['surge_amount'] + lm['breakdown']['surge_amount'],
#                 "total": fm['breakdown']['total'] + lm['breakdown']['total']
#             }

#             options.append({
#                 "type": f"Hybrid ({fm['mode']} + Metro + {lm['mode']})",
#                 "time": fm['time'] + metro_time + lm['time'],
#                 "cost": fm['cost'] + metro_total_fare + lm['cost'],
#                 "desc": f"{fm['mode']} to {metro_graph[start_stn]['name']} -> Metro to {metro_graph[end_stn]['name']} -> {lm['mode']} to Destination.",
#                 "metro_fare": f"DMRC: Rs {dmrc_f} + NMRC: Rs {aqua_f}" if aqua_f > 0 else f"DMRC: Rs {dmrc_f}",
#                 "cab_breakdown": combined_cab_breakdown,
#                 "time_breakdown": {"leg1": fm['time'], "metro": metro_time, "leg2": lm['time']},
#                 "leg1_mode": fm['mode'], "leg2_mode": lm['mode']
#             })

#     # --- 3. THE PARETO FILTER ---
#     pareto_optimal = []
#     for a in options:
#         if not any(b['time'] <= a['time'] and b['cost'] < a['cost'] or b['time'] < a['time'] and b['cost'] <= a['cost'] for b in options if a != b):
#             pareto_optimal.append(a)

#     return pareto_optimal

# # ==========================================
# # 5. EXECUTION & TESTING
# # ==========================================
# if __name__ == "__main__":
#     # Test Case: Bennett University to Hazrat Nizamuddin
#     BENNETT_UNI = (28.4500, 77.5840)
#     NZM_STATION = (28.5880, 77.2530)
    
#     CONTEXT = {"time": "Evening Peak", "traffic": "High", "road": "Main Road"}

#     print("--- RADAR: MULTI-MODAL ROUTING ENGINE ---")
#     print(f"[INFO] Source: Bennett University | Dest: Hazrat Nizamuddin")
#     print(f"[INFO] Context: {CONTEXT['time']}, Traffic: {CONTEXT['traffic']}\n")
    
#     results = run_multimodal_engine(BENNETT_UNI[0], BENNETT_UNI[1], NZM_STATION[0], NZM_STATION[1], CONTEXT)
    
#     print("🎯 RECOMMENDED ROUTES (PARETO FRONTIER):")
#     for idx, r in enumerate(results, 1):
#         print(f"\n{idx}. {r['type']}")
#         print(f"   ⏱️ Total Time: {r['time']} mins")
        
#         # --- TIME SPLITS ---
#         tb = r['time_breakdown']
#         if "Direct" in r['type']:
#             icon = "🚶" if r['leg1_mode'] == "Walk" else "🚗"
#             print(f"       ↳ {icon} {r['leg1_mode']}: {tb['leg1']} mins")
#         else:
#             icon1 = "🚶" if r['leg1_mode'] == "Walk" else "🚗"
#             icon2 = "🚶" if r['leg2_mode'] == "Walk" else "🚗"
#             print(f"       ↳ {icon1} Leg 1: {tb['leg1']} mins | 🚇 Metro: {tb['metro']} mins | {icon2} Leg 2: {tb['leg2']} mins")

#         print(f"   💸 Total Cost: Rs. {r['cost']:.2f}")
        
#         # --- FARE SPLITS ---
#         cb = r['cab_breakdown']
#         if cb['total'] > 0:
#             print(f"       ↳ 🚕 Cab Split:   Base: Rs {cb['base']:.0f} | Dist: Rs {cb['distance_fare']:.0f} | Surge: Rs {cb['surge_amount']:.0f}")
        
#         if "metro_fare" in r:
#             print(f"       ↳ 🎫 Metro Split: {r['metro_fare']}")
            
#         print(f"   🗺️ Itinerary:  {r['desc']}")
















import json
import math
import heapq
import sys
import os
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# --- WINDOWS SAFETY ---
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

script_dir = os.path.dirname(os.path.abspath(__file__))
json_graph_path = os.path.join(script_dir, 'delhi_metro_graph_real.json')

# ==========================================
# 1. LOAD THE UNIFIED METRO GRAPH
# ==========================================
try:
    with open(json_graph_path, 'r', encoding='utf-8') as f:
        metro_graph = json.load(f)
except FileNotFoundError:
    print(f"[ERROR] Graph missing: '{json_graph_path}'")
    sys.exit()

# ==========================================
# 2. THE EXTERNAL CAB ENGINE (TOMTOM + SELENIUM)
# ==========================================
class ExternalCabEngine:
    def __init__(self, tomtom_key):
        self.tomtom_key = tomtom_key
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3") 
        self.chrome_options = chrome_options

    def get_route_info(self, lat1, lon1, lat2, lon2):
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{lat1},{lon1}:{lat2},{lon2}/json"
        params = {"key": self.tomtom_key, "traffic": "true", "travelMode": "car"}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if "routes" in data:
                route = data["routes"][0]["summary"]
                return route["lengthInMeters"] / 1000.0, route["travelTimeInSeconds"] / 60.0
        except Exception as e:
            pass
        return None, None

    def get_scraped_price(self, start_query, end_query):
        driver = webdriver.Chrome(options=self.chrome_options)
        try:
            driver.get("https://www.taxi-calculator.com/")
            time.sleep(2)

            start = driver.find_element(By.ID, "startAddress")
            end = driver.find_element(By.ID, "destinationAddress")

            start.send_keys(start_query)
            time.sleep(1.5)
            start.send_keys(Keys.DOWN, Keys.RETURN, Keys.TAB)

            end.send_keys(end_query)
            time.sleep(1.5)
            end.send_keys(Keys.DOWN, Keys.RETURN, Keys.TAB)

            for b in driver.find_elements(By.TAG_NAME, "button"):
                if "calculate" in b.text.lower():
                    driver.execute_script("arguments[0].click();", b)
                    break

            time.sleep(4) 
            text = driver.find_element(By.TAG_NAME, "body").text
            price_match = re.search(r"Rs\s*([\d.]+)", text)
            if price_match: return float(price_match.group(1))
        except Exception:
            pass
        finally:
            driver.quit()
        return None 

    def calculate_fallback_fare(self, distance_km):
        return 50.0 + (distance_km * 15.0)

# ==========================================
# 3. METRO ROUTING ENGINE
# ==========================================
AVG_SPEED_KMPH = 45.0       
DWELL_TIME_SEC = 25         
INITIAL_WAIT_SEC = 300      

def get_slab_fare(d):
    if d <= 2.0: return 11
    elif d <= 5.0: return 21
    elif d <= 12.0: return 32
    elif d <= 21.0: return 43
    elif d <= 32.0: return 54
    else: return 64

def calculate_accurate_fare(route):
    dmrc_dist, aqua_dist = 0.0, 0.0
    for i in range(len(route) - 1):
        curr_node, next_node = route[i], route[i+1]
        edge_dist = next(e["distance_km"] for e in metro_graph[curr_node]["connections"] if e["to"] == next_node)
        line_name = metro_graph[next_node]['line'].upper()
        if "AQUA" in line_name: aqua_dist += edge_dist
        else: dmrc_dist += edge_dist
    return get_slab_fare(dmrc_dist) + get_slab_fare(aqua_dist), get_slab_fare(dmrc_dist), get_slab_fare(aqua_dist)

def find_fastest_route(start_id, end_id):
    if start_id not in metro_graph or end_id not in metro_graph: return None, 0, 0
    pq = [(INITIAL_WAIT_SEC, start_id, 0.0)]
    min_times = {start_id: INITIAL_WAIT_SEC}
    came_from = {}

    while pq:
        current_time, current_node, current_dist = heapq.heappop(pq)
        if current_node == end_id:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start_id)
            return path[::-1], current_time, current_dist

        for edge in metro_graph[current_node]["connections"]:
            neighbor = edge["to"]
            edge_time_sec = int((edge["distance_km"] / AVG_SPEED_KMPH) * 3600) + DWELL_TIME_SEC if edge["type"] == "rail" else edge["time_sec"]
            new_time = current_time + edge_time_sec
            new_dist = current_dist + edge["distance_km"]

            if neighbor not in min_times or new_time < min_times[neighbor]:
                min_times[neighbor] = new_time
                came_from[neighbor] = current_node
                heapq.heappush(pq, (new_time, neighbor, new_dist))
    return None, 0, 0

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 
    a = math.sin(math.radians(lat2 - lat1) / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon1) / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def get_nearest_stations(lat, lon, k=2):
    distances = [(haversine(lat, lon, data['lat'], data['lon']), stn_id) for stn_id, data in metro_graph.items() if 'lat' in data]
    return sorted(distances)[:k]

# ==========================================
# 4. MULTI-MODAL McRAPTOR LOGIC
# ==========================================
def get_leg_options(start_coords, end_coords, start_name, end_name, cab_engine, leg_label="Leg"):
    options = []
    
    haversine_dist_km = haversine(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
    estimated_street_dist = haversine_dist_km * 1.3
    walk_time_mins = int((estimated_street_dist / 5.0) * 60) 
    
    # --- DETAILED LOGGING: GATEKEEPER ---
    if walk_time_mins <= 20:
        print(f"      🛡️ [GATEKEEPER] {leg_label}: Under 20 mins ({estimated_street_dist:.2f} km). Forcing WALK. API Blocked.")
        options.append({"mode": "Walk", "time": walk_time_mins, "cost": 0.0, "real_dist_km": estimated_street_dist})
    else:
        print(f"      🌐 [GATEKEEPER] {leg_label}: Over 20 mins ({estimated_street_dist:.2f} km). Forcing CAB. Calling APIs...")
        
        real_dist, real_time = cab_engine.get_route_info(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
        if real_dist is None:
            print("         ⚠️ [API WARNING] TomTom failed. Using local math fallback.")
            real_dist = estimated_street_dist
            real_time = int((real_dist / 25.0) * 60)
        else:
            print(f"         ✅ [API SUCCESS] TomTom: {real_dist:.2f} km | {real_time:.0f} mins with traffic.")

        print(f"         🤖 [SCRAPER] Fetching live cab fare for: {start_name[:15]}... -> {end_name[:15]}...")
        scraped_price = cab_engine.get_scraped_price(start_name, end_name)
        
        if scraped_price:
            print(f"         ✅ [SCRAPER SUCCESS] Found fare: Rs. {scraped_price}")
            final_cost = scraped_price
        else:
            print(f"         ⚠️ [SCRAPER WARNING] Failed. Using fallback math equation.")
            final_cost = cab_engine.calculate_fallback_fare(real_dist)
            
        options.append({"mode": "Cab", "time": int(real_time), "cost": final_cost, "real_dist_km": real_dist})
        
    return options

def run_multimodal_engine(start_lat, start_lon, start_name, end_lat, end_lon, end_name):
    # DROP YOUR TOMTOM API KEY HERE
    cab_engine = ExternalCabEngine(tomtom_key=os.getenv("TOMTOM_API_KEY")) 
    options = []
    start_coords, end_coords = (start_lat, start_lon), (end_lat, end_lon)

    print("\n==========================================")
    print("🚦 PHASE 1: EVALUATING DIRECT ROUTE")
    print("==========================================")
    direct_leg = get_leg_options(start_coords, end_coords, start_name, end_name, cab_engine, leg_label="Direct Route")[0]
    
    options.append({
        "type": f"Direct {direct_leg['mode']}", "time": direct_leg['time'], "cost": direct_leg['cost'], 
        "desc": f"{direct_leg['mode']} entire way ({direct_leg['real_dist_km']:.1f} km)", 
        "time_breakdown": {"leg1": direct_leg['time'], "metro": 0, "leg2": 0},
        "leg1_mode": direct_leg['mode'], "leg2_mode": None
    })

    print("\n==========================================")
    print("🚇 PHASE 2: EVALUATING HYBRID PERMUTATIONS")
    print("==========================================")
    start_stns = get_nearest_stations(start_lat, start_lon, k=1) 
    end_stns = get_nearest_stations(end_lat, end_lon, k=1)

    print(f"📍 Nearest Start Stations: {[metro_graph[s]['name'] for _, s in start_stns]}")
    print(f"📍 Nearest End Stations: {[metro_graph[s]['name'] for _, s in end_stns]}\n")

    for dist_to_start, start_stn in start_stns:
        for dist_to_end, end_stn in end_stns:
            stn1_name = metro_graph[start_stn]['name'] + " Metro Station"
            stn2_name = metro_graph[end_stn]['name'] + " Metro Station"
            
            print(f"🔄 TESTING COMBINATION: {stn1_name} -> {stn2_name}")
            start_stn_coords = (metro_graph[start_stn]['lat'], metro_graph[start_stn]['lon'])
            end_stn_coords = (metro_graph[end_stn]['lat'], metro_graph[end_stn]['lon'])

            fm = get_leg_options(start_coords, start_stn_coords, start_name, stn1_name, cab_engine, leg_label="First Mile")[0]
            lm = get_leg_options(end_stn_coords, end_coords, stn2_name, end_name, cab_engine, leg_label="Last Mile")[0]

            route, metro_time_sec, metro_dist = find_fastest_route(start_stn, end_stn)
            if not route: 
                print("      ❌ [METRO] No valid route found between these stations. Skipping.")
                continue
                
            metro_time = metro_time_sec // 60
            metro_total_fare, dmrc_f, aqua_f = calculate_accurate_fare(route)
            print(f"      🚆 [METRO] Route calculated: {metro_dist:.1f} km | {metro_time} mins | Fare: Rs {metro_total_fare}")

            options.append({
                "type": f"Hybrid ({fm['mode']} + Metro + {lm['mode']})",
                "time": fm['time'] + metro_time + lm['time'],
                "cost": fm['cost'] + metro_total_fare + lm['cost'],
                "desc": f"{fm['mode']} to {metro_graph[start_stn]['name']} -> Metro to {metro_graph[end_stn]['name']} -> {lm['mode']} to Destination.",
                "metro_fare": f"DMRC: Rs {dmrc_f} + NMRC: Rs {aqua_f}" if aqua_f > 0 else f"DMRC: Rs {dmrc_f}",
                "time_breakdown": {"leg1": fm['time'], "metro": metro_time, "leg2": lm['time']},
                "leg1_mode": fm['mode'], "leg2_mode": lm['mode']
            })

    print("\n==========================================")
    print("⚖️ PHASE 3: PARETO OPTIMIZATION")
    print("==========================================")
    print(f"Total Routes Generated: {len(options)}")
    
    pareto_optimal = []
    for a in options:
        is_dominated = False
        for b in options:
            if a != b:
                if (b['time'] <= a['time'] and b['cost'] < a['cost']) or (b['time'] < a['time'] and b['cost'] <= a['cost']):
                    is_dominated = True
                    break
        if not is_dominated:
            pareto_optimal.append(a)
        else:
            print(f"🗑️ [DELETED] '{a['type']}' (Cost: {a['cost']}, Time: {a['time']}) was dominated by a better route.")

    print(f"Optimal Routes Surviving: {len(pareto_optimal)}")
    return pareto_optimal

# ==========================================
# 5. EXECUTION & TESTING
# ==========================================
if __name__ == "__main__":
    
    START_LAT, START_LON = 28.4506108, 77.5839118
    START_NAME = "Bennett University Greater Noida"
    
    END_LAT, END_LON = 28.6314, 77.2194
    END_NAME = "Connaught Place Delhi"

    results = run_multimodal_engine(START_LAT, START_LON, START_NAME, END_LAT, END_LON, END_NAME)
    
    print("\n🎯 RECOMMENDED ROUTES (FINAL OUTPUT):")
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r['type']}")
        print(f"   ⏱️ Total Time: {r['time']} mins")
        
        tb = r['time_breakdown']
        if "Direct" in r['type']:
            icon = "🚶" if r['leg1_mode'] == "Walk" else "🚗"
            print(f"       ↳ {icon} {r['leg1_mode']}: {tb['leg1']} mins")
        else:
            icon1 = "🚶" if r['leg1_mode'] == "Walk" else "🚗"
            icon2 = "🚶" if r['leg2_mode'] == "Walk" else "🚗"
            print(f"       ↳ {icon1} Leg 1: {tb['leg1']} mins | 🚇 Metro: {tb['metro']} mins | {icon2} Leg 2: {tb['leg2']} mins")

        print(f"   💸 Total Cost: Rs. {r['cost']:.2f}")
        if "metro_fare" in r: print(f"       ↳ 🎫 Metro Split: {r['metro_fare']}")
        print(f"   🗺️ Itinerary:  {r['desc']}")