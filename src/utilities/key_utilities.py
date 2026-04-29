from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.exceptions import InvalidSignature
from utilities.hash_utilities import sha256_hash


# Sign the hashed data using RSA-PSS with SHA-256, using max length salt across the entire hash to prevent signature forgery
# Returns the raw bytes signature
def sign_hashed_data(private_key, hashed_data):
    return private_key.sign(
        hashed_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        utils.Prehashed(hashes.SHA256())
    )

# Returns the public key for the car with the given ID from keys.json
def get_public_key_for_id(keys, id):
    key_entry = keys.get(f"car_{id}")
    if not key_entry:
        return None
    
    # Convert public key from UTF-8 to bytes and return the public key object
    return serialization.load_pem_public_key(key_entry['public_key'].encode('utf-8'))

# Returns π(σ(h(d))) ?= h(d)
def verify_signature(public_key, data, signature):
    hashed_data = sha256_hash(data)
    try:
        # Verify the signature using RSA-PSS with SHA-256, using original max length salt across the entire hash
        public_key.verify(
            signature,
            hashed_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False  
