"""
TraCI script that listens for vehicles entering a radius from the RSU in an event-driven manner.
"""

"""
Extracted data: vehicle ID, speed, latitude, longitude, and timestamp.
In the current implementation, the RSU reports every time a vehicle enters the listening region (including re-entries).
The simulation is run for WALL_CLOCK_LIMIT seconds.
Data is piped to stdout as JSON for consumption by another program.
Usage:
    python rsu_listener_alt.py | python ../src/chain_generator.py
"""

import traci
import traci.constants as tc
from datetime import datetime
import time
import json
import sys
import base64
import os
from cryptography.hazmat.primitives import serialization
from utilities.hash_utilities import sha256_hash
from utilities.key_utilities import sign_hashed_data

# RSU configuration (from rsu.add.xml)
RSU_X = 605
RSU_Y = 226
RSU_RADIUS = 100  # listening range in meters

# Track vehicles already in region from previous simulation step to detect new entries
vehicles_previously_in_region = set()

total_reports_processed = 0

script_dir = os.path.dirname(os.path.abspath(__file__))
keys_path = os.path.join(script_dir, "../../generated_data/keys.json")

try:
    with open(keys_path, "r") as f:
        vehicle_keys = json.load(f)
    print(f"Loaded {len(vehicle_keys)} vehicle key pairs from {keys_path}", file=sys.stderr)
except FileNotFoundError:
    print(f"Error: Vehicle keys file not found at {keys_path}. Cannot continue without keys.", file=sys.stderr)
    sys.exit(1)


def get_geo_coordinates(x, y):
    try:
        lon, lat = traci.simulation.convertGeo(x, y, fromGeo=False)
        return lat, lon
    except:
        return None, None


def process_subscription_results():
    global vehicles_previously_in_region, total_reports_processed

    # Get subscription results from POI context subscription
    context_results = traci.poi.getContextSubscriptionResults("RSU_1")
    
    # Vehicles in current simulation step
    current_vehicles = set()
    
    # context_results is a dict: {vehicle_id: {variable_id: value, ...}}
    for vehicle_id, vehicle_data in context_results.items():
        current_vehicles.add(vehicle_id)
        
        # Check if this is a new entry (vehicle wasn't in region before)
        if vehicle_id not in vehicles_previously_in_region:
            
            # Capture timestamp at moment of first appearance
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                        
            speed = vehicle_data.get(tc.VAR_SPEED)
            x, y = vehicle_data.get(tc.VAR_POSITION)
            lat, lon = get_geo_coordinates(x, y)
            
            if speed is None or lat is None or lon is None:
                print(f"Skipping vehicle {vehicle_id} due to missing data", file=sys.stderr)
                continue

            data = {
                "id": vehicle_id,
                "vel": round(speed * 3.6, 2),
                "lat": lat, 
                "lon": lon,
                "ts": timestamp
            }

            #TODO: Sign the data with the vehicle's private key (simulating vehicle-side signing)

            total_reports_processed += 1

            # Pipe to stdout as JSON
            print(json.dumps(data))
            sys.stdout.flush()
    
    # Update for comparison with next simulation step
    vehicles_previously_in_region = current_vehicles


def main():
    sumo_cmd = ["sumo-gui", "-c", "map.sumocfg"]
    traci.start(sumo_cmd)
    
    print(f"Starting RSU listener at position ({RSU_X}, {RSU_Y}) with {RSU_RADIUS}m radius", file=sys.stderr)
    print("=" * 100, file=sys.stderr)
    
    # Setup subscription context for notifications from region around RSU
    traci.poi.subscribeContext(
        "RSU_1",
        tc.CMD_GET_VEHICLE_VARIABLE,  
        RSU_RADIUS,    
        [  
            tc.VAR_SPEED,      
            tc.VAR_POSITION,   
        ]
    )
    
    print("Context subscription established. Listening for vehicles...", file=sys.stderr)
    print("=" * 100, file=sys.stderr)
    
    step = 0
    start_time = time.time()
    WALL_CLOCK_LIMIT = 30  #seconds
    
    while traci.simulation.getMinExpectedNumber() > 0:
        elapsed_time = time.time() - start_time
        if elapsed_time >= WALL_CLOCK_LIMIT:
            print(f"\nWall clock time limit of {WALL_CLOCK_LIMIT}s reached.", file=sys.stderr)
            break
        
        traci.simulationStep()
        process_subscription_results()
        step += 1

    traci.close()
    print(f"\nSimulation ended after {step} steps.", file=sys.stderr)
    print(f"\n" + "=" * 100, file=sys.stderr)
    print(f"Total reports processed: {total_reports_processed}", file=sys.stderr)

if __name__ == "__main__":
    main()
