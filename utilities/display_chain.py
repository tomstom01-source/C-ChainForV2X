import sqlite3



def display_chain_info():
    connection = sqlite3.connect('generated_data/V2X_chain.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, signed_prev_block_hash, signed_transaction FROM transaction_blocks ORDER BY id ASC')
    blocks = cursor.fetchall()
    
    for block_id, signed_prev_block_hash, signed_transaction in blocks:
        print(f"\nBlock {block_id}:")
        if len(signed_prev_block_hash) > 50:
            print(f"    Signed Prev Block Hash: {signed_prev_block_hash[:50]}...")
        else:
            print(f"    Signed Prev Block Hash: {signed_prev_block_hash}")
        if len(signed_transaction) > 50:
            print(f"    Signed Transaction: {signed_transaction[:50]}...")
        else:
            print(f"    Signed Transaction: {signed_transaction}")
   
    connection.close()