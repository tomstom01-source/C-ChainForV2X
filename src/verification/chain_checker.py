import json
import sqlite3
import base64
from cryptography.hazmat.primitives import serialization
from utilities.key_utilities import verify_signature


# Check chain continuity: πS(σS(h(prev_block))) ?= h(prev_block)
def check_continuity(cursor, block_id, signed_prev_block_hash, tdbms_public_key):
    if block_id == 1:
        return signed_prev_block_hash == "0" * 64

    # Get previous block
    cursor.execute('SELECT signed_prev_block_hash, signed_transaction FROM transaction_blocks WHERE id = ?', (block_id - 1,))
    prev_block = cursor.fetchone()
   
    if not prev_block:
        print(f"Previous block {block_id - 1} not found in table")
        return False 
    prev_block_signed_prev_block_hash, prev_block_signed_transaction = prev_block
    expected_prev_block = {
        "id": block_id - 1,
        "signed_prev_block_hash": prev_block_signed_prev_block_hash,
        "signed_transaction": prev_block_signed_transaction
    }
    actual_signature = base64.b64decode(signed_prev_block_hash)
    return verify_signature(public_key=tdbms_public_key, data=expected_prev_block, signature=actual_signature)


# Runs a simple chain test by checking each block for:
#  - πS(σS(h(prev_block))) ?= h(prev_block): Continuity check
#  - LATER, possibly also πS(σS(σU(h(d)))) ?= σU(h(d)) by storing σU(h(d))s in another file: Payload check
def check_chain():
    
    # Load TDBMS public key
    with open("../generated_data/tdbms_keys.json", "r") as f:
        tdbms_keys = json.load(f)
    
    tdbms_public_key = serialization.load_pem_public_key(tdbms_keys['public_key'].encode('utf-8'))
    
    # Connect to database
    connection = sqlite3.connect('../generated_data/V2X_chain.db')
    cursor = connection.cursor()
    
    # Get all blocks in asc order
    cursor.execute('SELECT id, signed_prev_block_hash, signed_transaction FROM transaction_blocks ORDER BY id ASC')
    # Batch-process here for scaling
    blocks = cursor.fetchall()
    
    print(f"Found {len(blocks)} blocks in chain.")
    
    validated_blocks = 0
    for block_id, signed_prev_block_hash, _ in blocks:
        if check_continuity(cursor, block_id, signed_prev_block_hash, tdbms_public_key):
            validated_blocks += 1
        else:
            print(f"Block {block_id} continuity check failed")
    
    connection.close()
    print("\n" + "=" * 100)
    print(f"Processed {len(blocks)} blocks. Validated {validated_blocks} blocks for continuity.")
    print("=" * 100)
    return True