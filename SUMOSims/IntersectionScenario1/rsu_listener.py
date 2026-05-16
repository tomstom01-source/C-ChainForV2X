"""
TraCI script that listens for vehicles entering a radius from the RSU in an event-driven manner.
"""

"""
Extracted data: vehicle ID, speed, latitude, longitude, and timestamp.
In the current implementation, the RSU reports every time a vehicle enters the listening region (including re-entries).
Latitude and longitude default back to x and y coordinates in the absence of geo-referencing data.
The simulation is run for WALL_CLOCK_LIMIT seconds.
Usage:
    python rsu_listener.py
"""

import traci
import traci.constants as tc
from datetime import datetime
import time

# RSU configuration (from rsu.add.xml)
RSU_X = 605
RSU_Y = 226
RSU_RADIUS = 100  # listening range in meters

# Track vehicles already in region from previous simulation step to detect new entries
vehicles_previously_in_region = set()

total_reports_processed = 0


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
            
            total_reports_processed += 1
            
            speed = vehicle_data.get(tc.VAR_SPEED)
            x, y = vehicle_data.get(tc.VAR_POSITION)
            lat, lon = get_geo_coordinates(x, y)
            
            if speed is None or x is None or y is None:
                print(f"Vehicle: {vehicle_id} - Missing data")
                continue
            
            print(f"Vehicle: {vehicle_id}")
            print(f"  Speed: {speed * 3.6:.2f} km/h")
            if lat is not None and lon is not None:
                print(f"  Position (geo): lat={lat:.7f}, lon={lon:.7f}")
            else:
                print(f"  Position (network): x={x:.2f}, y={y:.2f}")
            print(f"  Timestamp: {timestamp}")
            print("-" * 100)
    
    # Update for comparison with next simulation step
    vehicles_previously_in_region = current_vehicles


def main():
    sumo_cmd = ["sumo-gui", "-c", "map.sumocfg"]
    traci.start(sumo_cmd)
    
    print(f"Starting RSU listener at position ({RSU_X}, {RSU_Y}) with {RSU_RADIUS}m radius")
    print("=" * 100)
    
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
    
    print("Context subscription established. Listening for vehicles...")
    print("=" * 100)
    
    step = 0
    start_time = time.time()
    WALL_CLOCK_LIMIT = 30  #seconds
    
    while traci.simulation.getMinExpectedNumber() > 0:
        elapsed_time = time.time() - start_time
        if elapsed_time >= WALL_CLOCK_LIMIT:
            print(f"\nWall clock time limit of {WALL_CLOCK_LIMIT}s reached.")
            break
        
        traci.simulationStep()
        process_subscription_results()
        step += 1

    traci.close()
    print(f"\nSimulation ended after {step} steps.")
    print(f"\n" + "=" * 100)
    print(f"Total reports processed: {total_reports_processed}")

if __name__ == "__main__":
    main()
