# vault.py
# Project ANACONDA Vault Dependency Manager v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import os
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

VAULT_DIR = r"C:\RegimeOS\language\anaconda"
STD_LIB_DIR = os.path.join(VAULT_DIR, "src", "stdlib")
MANIFEST_PATH = os.path.join(VAULT_DIR, "manifest.json")
SIGNATURE_PATH = os.path.join(VAULT_DIR, "manifest.sig")
KEY_DIR = os.path.join(VAULT_DIR, "keys")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "armada_signing_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "armada_signing_key.pub")

os.makedirs(STD_LIB_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

def generate_key_pair():
    """Generates an Ed25519 key pair for Armada XVII Code Signing if not already present."""
    if not os.path.exists(PRIVATE_KEY_PATH):
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Save Private Key
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save Public Key
        public_key = private_key.public_key()
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print("[*] Generated new Armada XVII Code Signing Ed25519 keypair.")

def load_private_key():
    generate_key_pair()
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key():
    generate_key_pair()
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def calculate_sha384(filepath: str) -> str:
    h = hashlib.sha384()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def scan_for_network_imports(content: str) -> list[str]:
    """Scans code content for prohibited modules (requests, urllib, socket, etc.)."""
    prohibited = {"requests", "urllib", "http", "socket", "aiohttp", "pika", "ftplib", "smtplib"}
    found = []
    import ast
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.split('.')[0]
                    if name in prohibited:
                        found.append(name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    name = node.module.split('.')[0]
                    if name in prohibited:
                        found.append(name)
    except Exception:
        # Fallback to regex/simple check if AST parsing fails
        for p in prohibited:
            if f"import {p}" in content or f"from {p}" in content:
                found.append(p)
    return list(set(found))

def vendor_library(source_path: str, lib_name: str):
    """Vendors a library into the standard library folder, checking for network code."""
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    network_libs = scan_for_network_imports(content)
    if network_libs:
        raise PermissionError(f"Security Violation: Module contains prohibited network imports: {network_libs}")

    dest_path = os.path.join(STD_LIB_DIR, lib_name)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Vendored library: {lib_name}")
    generate_manifest()

def generate_manifest():
    """Generates manifest.json of all stdlib files and signs it in manifest.sig."""
    files_to_hash = {}
    
    # Gather all files in kernel, compiler, and stdlib
    for root_dir in [os.path.join(VAULT_DIR, "src", "kernel"), os.path.join(VAULT_DIR, "src", "compiler"), STD_LIB_DIR]:
        if not os.path.exists(root_dir):
            continue
        for root, dirs, files in os.walk(root_dir):
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            for file in files:
                if file.endswith((".pyc", ".pyo")):
                    continue
                full_path = os.path.join(root, file)
                # Store path relative to VAULT_DIR with forward slashes for cross-platform compliance
                rel_path = os.path.relpath(full_path, VAULT_DIR).replace("\\", "/")
                files_to_hash[rel_path] = calculate_sha384(full_path)

    # Sort files to ensure determinism
    sorted_files = {k: files_to_hash[k] for k in sorted(files_to_hash.keys())}
    
    # Compute the hash of all hashes
    h_all = hashlib.sha384()
    for rel_path, h_val in sorted_files.items():
        h_all.update(rel_path.encode('utf-8'))
        h_all.update(h_val.encode('utf-8'))
    manifest_hash = h_all.hexdigest()

    manifest_data = {
        "files": sorted_files,
        "manifest_hash": manifest_hash
    }

    # Write manifest.json
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)

    # Sign the manifest hash
    private_key = load_private_key()
    signature = private_key.sign(manifest_hash.encode('utf-8'))

    with open(SIGNATURE_PATH, "wb") as f:
        f.write(signature)

    print(f"[+] Successfully generated and signed manifest for {len(sorted_files)} files.")

def verify_vault_integrity() -> bool:
    """Verifies that all files match the signed manifest hashes and the signature is valid."""
    if not os.path.exists(MANIFEST_PATH) or not os.path.exists(SIGNATURE_PATH):
        print("[!] Validation failed: Manifest or Signature file is missing.")
        return False

    # Load Manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    sorted_files = manifest_data.get("files", {})
    manifest_hash = manifest_data.get("manifest_hash", "")

    # 1. Verify every file matches its hash
    h_all = hashlib.sha384()
    for rel_path, expected_hash in sorted_files.items():
        full_path = os.path.join(VAULT_DIR, rel_path.replace("/", "\\"))
        if not os.path.exists(full_path):
            print(f"[!] Validation failed: Missing file: {rel_path}")
            return False
        
        actual_hash = calculate_sha384(full_path)
        if actual_hash != expected_hash:
            print(f"[!] Validation failed: Hash mismatch for {rel_path}")
            return False

        h_all.update(rel_path.encode('utf-8'))
        h_all.update(actual_hash.encode('utf-8'))

    calculated_manifest_hash = h_all.hexdigest()
    if calculated_manifest_hash != manifest_hash:
        print("[!] Validation failed: Calculated manifest hash mismatch.")
        return False

    # 2. Verify signature
    with open(SIGNATURE_PATH, "rb") as f:
        signature = f.read()

    public_key = load_public_key()
    try:
        public_key.verify(signature, calculated_manifest_hash.encode('utf-8'))
        print("[+] SUCCESS: Chain of custody verification PASSED. Binary and scripts match signed manifest.")
        return True
    except Exception as e:
        print(f"[!] Validation failed: Ed25519 signature mismatch: {e}")
        return False

def sign_air_file(file_path: str):
    """Signs an .air file by appending `# SIGNATURE: <hex>` block at the end."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Strip any trailing signature line
    if lines and lines[-1].startswith("# SIGNATURE:"):
        lines = lines[:-1]
    
    content = "".join(lines)
    # Strip trailing whitespace to ensure a standard state
    content = content.rstrip() + "\n"
    
    # Generate signature
    private_key = load_private_key()
    signature = private_key.sign(content.encode("utf-8"))
    sig_hex = signature.hex()
    
    signed_content = content + f"# SIGNATURE: {sig_hex}\n"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(signed_content)
    
    print(f"[+] Signed code file: {file_path}")

def verify_air_signature(file_path: str) -> bool:
    """Verifies the Ed25519 signature appended to the end of an .air file."""
    if not os.path.exists(file_path):
        print(f"[!] Signature validation failed: file not found: {file_path}")
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    if not lines or not lines[-1].startswith("# SIGNATURE:"):
        print(f"[!] Signature validation failed: no signature comment found in {file_path}")
        return False
        
    sig_line = lines[-1]
    sig_hex = sig_line.replace("# SIGNATURE:", "").strip()
    
    # Rest of the content before signature comment
    content = "".join(lines[:-1])
    content = content.rstrip() + "\n"
    
    try:
        sig_bytes = bytes.fromhex(sig_hex)
        public_key = load_public_key()
        public_key.verify(sig_bytes, content.encode("utf-8"))
        return True
    except Exception as e:
        print(f"[!] Signature verification failed for {file_path}: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        success = verify_vault_integrity()
        sys.exit(0 if success else 1)
    else:
        generate_manifest()
