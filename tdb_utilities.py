import sqlite3



def setup_tdb():
    connection = sqlite3.connect('V2X_chain.db')
    cursor = connection.cursor()
    # Each block (or "chain link") consists of:
    # - id (the block id)
    # - signed_prev_block_hash: σS(h(prev_block))
    # - signed_transaction: σS(T) = {d, σS(σU(h(d)))}
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signed_prev_block_hash TEXT,
            signed_transaction TEXT
        )
    ''')
    connection.commit()
    return connection


# Returns a dict entry of the last block in the chain or None if chain is empty.
def get_last_block(cursor):
    cursor.execute('SELECT id, signed_prev_block_hash, signed_transaction FROM transaction_blocks ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    if not result:
        return None
    last_block = {"id": result[0], "signed_prev_block_hash": result[1], 
                      "signed_transaction": result[2]}
    return last_block