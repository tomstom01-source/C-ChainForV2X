import sqlite3

def display_block(block):
    block_id, signed_prev_block_hash, signed_transaction = block
    print(f"\nBlock {block_id}:")
    if len(signed_prev_block_hash) > 50:
        print(f"    Signed Prev Block Hash: {signed_prev_block_hash[:50]}...")
    else:
        print(f"    Signed Prev Block Hash: {signed_prev_block_hash}")
    if len(signed_transaction) > 50:
        print(f"    Signed Transaction: {signed_transaction[:50]}...")
    else:
        print(f"    Signed Transaction: {signed_transaction}")

def display_chain_info():
    connection = sqlite3.connect('generated_data/V2X_chain.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, signed_prev_block_hash, signed_transaction FROM transaction_blocks ORDER BY id ASC')
    blocks = cursor.fetchall()
    
    # Display first 5 blocks
    for i in range(min(5, len(blocks))):
        display_block(blocks[i])
    
    remaining_blocks = len(blocks) - min(5, len(blocks))
    
    if remaining_blocks > 5:
        skipped_blocks = remaining_blocks - 5
        print("\n" + "=" * 100)
        print(f"... (skipped showing {skipped_blocks} blocks) ...")
        print("=" * 100 + "\n")
        
    # Display last 5 blocks
    if remaining_blocks > 0:
        start_index = len(blocks) - min(5, remaining_blocks)
        for i in range(start_index, len(blocks)):
            display_block(blocks[i])
   
    connection.close()