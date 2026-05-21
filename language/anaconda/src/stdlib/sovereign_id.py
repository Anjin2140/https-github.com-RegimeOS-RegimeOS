# sovereign_id.py
# Project ANACONDA Sovereign Identity Module v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import sys
import os

# Insert vendored directory to sys.path to resolve keyring
stdlib_dir = os.path.dirname(os.path.abspath(__file__))
vendor_dir = os.path.join(stdlib_dir, "vendor")
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

import keyring
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

SERVICE_NAME = "ANACONDA_Sovereign_ID"
USERNAME = "local_node"

def get_sovereign_key() -> ed25519.Ed25519PrivateKey:
    """Retrieves or generates the Ed25519 sovereign private key from Windows Credential Manager."""
    priv_pem = keyring.get_password(SERVICE_NAME, USERNAME)
    if priv_pem:
        try:
            return serialization.load_pem_private_key(priv_pem.encode('utf-8'), password=None)
        except Exception:
            # If corruption occurs, clear and regenerate
            pass
            
    # Generate new key pair
    private_key = ed25519.Ed25519PrivateKey.generate()
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    keyring.set_password(SERVICE_NAME, USERNAME, pem_bytes.decode('utf-8'))
    return private_key

def get_public_key_bytes() -> bytes:
    """Returns the raw public key bytes of the sovereign identity."""
    private_key = get_sovereign_key()
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

def sign_data(data: bytes) -> bytes:
    """Signs the provided data using the local sovereign identity key."""
    private_key = get_sovereign_key()
    return private_key.sign(data)

def verify_signature(pub_bytes: bytes, signature: bytes, data: bytes) -> bool:
    """Verifies a signature against data and raw public key bytes."""
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        public_key.verify(signature, data)
        return True
    except Exception:
        return False
