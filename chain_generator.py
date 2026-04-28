import time
from datetime import datetime
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from tdb_utilities import setup_tdb, get_last_block
from key_utilities import get_public_key_for_id, verify_signature, sign_hashed_data
from hash_utilities import sha256_hash



# This just loads transactions from the JSON file all together 
# A more realistic simulation would involve transactions being fired sporadically at high frequency 
# and appropriate multithreading for the transaction "shooter" and transaction "processor" if simulated on the same device.
# Steps 4 and 5 in the protocol (synchronizing the TC at U's and V's sides) are not implemented in this simple simulation.
def process_transactions(transactions_filename, connection, tdbms_key_pair):
    skipped_transactions = 0
    with open(transactions_filename, "r") as f:
        transactions = json.load(f)
    with open("keys.json", "r") as f:
        keys = json.load(f)
    tdbms_private_key = serialization.load_pem_private_key(tdbms_key_pair["private_key"].encode('utf-8'), password=None)
    cursor = connection.cursor()

    # Create a Genesis block if chain doesn't exist yet
    # Genesis block : {"id": 1, "signed_prev_block_hash": "0" * 64
    #                           , "signed_transaction": {d, σS(h(d)}}
    # where d = "Genesis block created at (YYYY-MM-DDTHH:MM:SS.ssssss) by owner of public key (public_key of TDBMS, πS)"
    # "signed_transaction": {d, σS(h(d)} in the Genesis block allows non-repudiation of TDBMS for creating the Genesis block 
    # and thereby, the chain
    cursor.execute("SELECT COUNT(*) FROM transaction_blocks")
    if cursor.fetchone()[0] == 0:
        print("Creating Genesis block.")
        d = f"Genesis block created at {datetime.fromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%S.%f")} by owner of public key {tdbms_key_pair['public_key']}"
        Genesis_block = {"signed_prev_block_hash": "0" * 64,
                         "signed_transaction": json.dumps({"data": d, 
                                        "signature": base64.b64encode(sign_hashed_data(private_key=tdbms_private_key, 
                                                        hashed_data=sha256_hash(d))).decode('utf-8')}, 
                                        sort_keys=True, separators=(',', ':'))}
        cursor.execute('''
            INSERT INTO transaction_blocks (signed_prev_block_hash, signed_transaction) 
                       VALUES (?, ?)
        ''', (Genesis_block["signed_prev_block_hash"], Genesis_block["signed_transaction"]))

    for transaction in transactions:
        data = transaction["data"]
        
        if not data or not transaction["signature"]:
            print("Invalid transaction format. Skipping.")
            skipped_transactions += 1
            continue
        # Get raw bytes signature
        signature = base64.b64decode(transaction["signature"])
        public_key = get_public_key_for_id(keys=keys, id=data["id"])
        if not public_key:
            print(f"No public key found for car with ID {data['id']}. Skipping.")
            skipped_transactions += 1
            continue
        
        # Check πU(σU(h(d))) ?= h(d)
        if not verify_signature(public_key=public_key, data=data, signature=signature):
            print(f"Invalid signature for car with ID {data['id']}. Skipping.")
            skipped_transactions += 1
            continue
        
        # Signing by TDBMS: σS(h(σU(h(d))))
        # tdbms_signed_transaction = σS(T) = {d, σS(h(σU(h(d))))}
        tdbms_signed_transaction ={"data": data, 
                                   "signature": base64.b64encode(sign_hashed_data(private_key=tdbms_private_key, 
                                                    hashed_data=sha256_hash(signature))).decode('utf-8')}

        last_block = get_last_block(cursor=cursor)
                
        cursor.execute('''
            INSERT INTO transaction_blocks (signed_prev_block_hash, signed_transaction) 
                       VALUES (?, ?)
        ''', (base64.b64encode(sign_hashed_data(private_key=tdbms_private_key, 
                            hashed_data=sha256_hash(last_block))).decode('utf-8'),
                json.dumps(tdbms_signed_transaction, sort_keys=True, separators=(',', ':'))))

    if skipped_transactions > 0:
        print(f"Skipped {skipped_transactions} incompatible transactions.")           
    
    connection.commit()


def generate_chain(transactions_filename):
    connection = setup_tdb()

    #TDBMS keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    tdbms_key_pair = {"private_key": private_key.private_bytes(
                                        encoding=serialization.Encoding.PEM,
                                        format=serialization.PrivateFormat.PKCS8,
                                        encryption_algorithm=serialization.NoEncryption()
                                        ).decode('utf-8'), 
                        "public_key": public_key.public_bytes(
                                        encoding=serialization.Encoding.PEM,
                                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                                        ).decode('utf-8')}
    with open("tdbms_keys.json", "w") as f:
        json.dump(tdbms_key_pair, f)
    print("Successfully generated TDBMS key pair in tdbms_keys.json.")
    
    process_transactions(transactions_filename=transactions_filename, connection=connection, tdbms_key_pair = tdbms_key_pair)
    
    print("Finished processing transactions.")
    connection.close()
