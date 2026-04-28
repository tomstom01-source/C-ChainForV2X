import hashlib
import json



# Canonicalizes input, converts to bytes, hashes and returns digest based on input type
def sha256_hash(data):
    if isinstance(data, dict):
        canonicalized_data = json.dumps(data, sort_keys=True, separators=(',', ':')).encode("utf-8")
    elif isinstance(data, str):
        canonicalized_data = data.encode("utf-8")
    elif isinstance(data, bytes):
        canonicalized_data = data
    else:
        raise TypeError(f" Unsupported data type for hashing: {type(data).__name__}. Supported types are dict, str, and bytes.")

    return hashlib.sha256(canonicalized_data).digest()
