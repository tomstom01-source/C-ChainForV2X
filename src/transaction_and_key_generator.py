import json
import random
import time
import base64
import os
from datetime import datetime
from utilities.hash_utilities import sha256_hash
from utilities.key_utilities import sign_hashed_data
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa



# Transactions are written into the passed filename and keys are always stored in keys.json.
# UDB is yet to be implemented
def generate_mock_transactions_and_keys(transactions_filename, number_of_cars, transactions_per_car):
    print("Chosen parameters:")
    print(f"  Number of cars: {number_of_cars}")
    print(f"  Transactions per car: {transactions_per_car}")
    print(f"  Transactions file: {transactions_filename}")
    
    # Current time to start random timestamp generation
    start_time = time.time()
    
    # Locality (example: Boltzmannstraße/Lichtenbergstraße junction, Garching)
    center_lat = 48.2667049
    center_lon = 11.67180061
    # 0.001 degrees is roughly 100 meters
    spread = 0.000549286  

    transactions = []
    
    # Create a dictionary of dictionaries to store key pairs for fast indexing
    key_pairs = {}
    
    for i in range(number_of_cars):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        # Use appropriate encoding and formatting for keys and decode to UTF-8 for JSON storage
        key_pairs[f"car_{i}"] = {"private_key": private_key.private_bytes(
                                                    encoding=serialization.Encoding.PEM,
                                                    format=serialization.PrivateFormat.PKCS8,
                                                    encryption_algorithm=serialization.NoEncryption()
                                                    ).decode('utf-8'), 
                                    "public_key": public_key.public_bytes(
                                                        encoding=serialization.Encoding.PEM,
                                                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                                                    ).decode('utf-8')}
        for _ in range(transactions_per_car):
            # Simulate time progression with random spacing at millisecond precision according to YYYY-MM-DDTHH:MM:SS.sss format
            timestamp = datetime.fromtimestamp(start_time + 
                                               random.uniform(0.001, 0.1)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            data = {
                "id": i,
                # Rounding to 7 decimal places for realistic GPS precision
                "lat": round(random.uniform(center_lat - spread, center_lat + spread), 7),
                "lon": round(random.uniform(center_lon - spread, center_lon + spread), 7),
                
                "vel": round(random.uniform(0.0, 450.0), 2),
                "ts": timestamp
            }
            # T = {d,σU(h(d))}
            # Base64 encode the raw bytes signature and decode to UTF-8 for JSON storage
            transactions.append({"data": data, 
                                 "signature": base64.b64encode(sign_hashed_data(private_key=private_key, 
                                                                                hashed_data=sha256_hash(data))).decode("utf-8")})
    
    # Ensure generated_data directory exists at project root
    os.makedirs("generated_data", exist_ok=True)
    
    # Convert keys to a JSON file
    with open("generated_data/keys.json", "w") as f:
        json.dump(key_pairs, f)

    print(f"Successfully generated {len(key_pairs)} key pairs in generated_data/keys.json.")
    
    # Shuffle transactions between cars
    random.shuffle(transactions)

    # Convert transactions to a JSON file
    with open(f"generated_data/{transactions_filename}", "w") as f:
        json.dump(transactions, f)

    print(f"Successfully generated {len(transactions)} transactions in generated_data/{transactions_filename}.")