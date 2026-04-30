# C-ChainForV2X

An initial implementation of the C-Chain system for secure logging and verification of V2X (Vehicle-to-Everything) communication, as described in C-ChainPaper.pdf.

## Overview

This project partially implements the cryptographic chaining protocol defined in the "Protocol of TDBMS" section of the C-Chain paper. The system provides immutable and verifiable logging of V2X transactions with cryptographic guarantees of integrity and non-repudiation.

TODO: transaction structure, output example

## Architecture & Control Flow

### Components Summary

#### 1. **Utilities**
- `hash_utilities.py`: SHA-256 canonicalization and hashing
- `key_utilities.py`: RSA-PSS signature generation/verification
- `tdb_utilities.py`: SQLite database management
- `display_chain.py`: Chain visualization and inspection

#### 2. **Generators**
- `transaction_and_key_generator.py`: Mock V2X transaction simulation
- `chain_generator.py`: Transaction validation and block creation

#### 3. **Verification**
- `chain_checker.py`: Chain continuity verification
  
#### 4. **Storage**
- `generated_data/keys.json`: Vehicle RSA key pairs
- `generated_data/tdbms_keys.json`: TDBMS RSA key pair
- `generated_data/mock_transactions.json`: Generated V2X transaction data
- `generated_data/V2X_chain.db`: SQLite database containing the blockchain


### Flow Summary

1. **Vehicle Generation**: Vehicles (cars) generate V2X transactions containing:
   - GPS coordinates (lat, lon)
   - Velocity data
   - Timestamp
   - Digital signature using vehicle's private key

2. **TDBMS Validation**: The TDBMS:
   - Verifies vehicle signatures using public keys
   - Signs the vehicle's signature with TDBMS private key
   - Creates a new block linked to the previous block

3. **Block Structure**: Each block contains:
   ```json
   {
     "id": block_number,
     "signed_prev_block_hash": "TDBMS_signature_of_previous_block_hash",
     "signed_transaction": {
       "data": "original_v2x_transaction_data",
       "signature": "TDBMS_signature_over_vehicle_signature"
     }
   }
   ```

4. **Genesis Block**: The first block (ID=0) with:
   - `signed_prev_block_hash = "0"*64`
   - Creation timestamp and TDBMS public key reference

## Security Properties

### Cryptographic Guarantees

1. **Immutability**: Each block is cryptographically linked to its predecessor
2. **Non-repudiation**: TDBMS signatures provide undeniable proof of transaction processing
3. **Integrity**: Any tampering breaks the cryptographic chain
4. **Authenticity**: Vehicle signatures ensure transaction authenticity

### Cryptographic Standards

- **Hash Algorithm**: SHA-256
- **Signature Scheme**: RSA-PSS with maximum salt length
- **Key Size**: 2048-bit RSA keys
- **Encoding**: PEM format for keys, Base64 for signatures

### Verification Process

The system verifies continuity of the chain by checking:
`πS(σS(h(prev_block))) ?= h(prev_block)`

## Usage

```python
# Available arguments:
#   -f: transactions output filename
#   -c: number of cars
#   -t: number of transactions per car

# An example to generate mock transactions, process them into the chain, and verify the chain
python src/main.py -f transactions.json -c 50 -t 20


# Alternatively, use:
python src/main.py --help
```

## Console Output Example

![Terminal Output](assets/images/console-output-example.png)

## Implementation Notes

### Protocol Steps

    The current implementation covers Steps 1-3 of the TDBMS protocol (page 9 of the paper):
    ✅ Verifying T = [d, σU(h(d))] by checking πU(σU(h(d))) ?= h(d)
    ✅ Certification	of T via σS(T) = [d, σS(σU(h(d)))]
    ✅ Appending T into blocks as [n+1, σS(h(Tn)), σS(T)]
   
### TBD

    ⚠️ Checking blocks in chain for not just continuity, but also payload integrity via πS(σS(σU(h(d)))) ?= σU(h(d)) while allowing RSA-PSS for σU(h(d))
    ⚠️ UDB with CryptIDs
    ⚠️ Steps 4-5 of the TDBMS protocol (TC synchronization at cars)
    ⚠️ Simulation of nodes via SUMO instead of loading transactions from a file
    ⚠️ Performance optimization and benchmarking
    ⚠️ PostgreSQL 
