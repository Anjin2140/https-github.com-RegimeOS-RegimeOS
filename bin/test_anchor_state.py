# C:\RegimeOS\bin\test_anchor_state.py
# ==============================================================================
# SovereignVault VaaS State Anchoring Test Execution
# Product of Armada XVII | Owned & Operated by Christopher E. Adams
# ==============================================================================
import os
import sys
import json
from pathlib import Path
import solcx
from web3 import Web3

# Add bin path
sys.path.insert(0, str(Path(__file__).parent.absolute()))
from secret_manager import get_secret
from muji_web3_arbiter import MujiWeb3Arbiter

def main():
    print("=" * 80)
    print("            ARMADA XVII - VAAS STATE ANCHOR TEST EXECUTION")
    print("=" * 80)

    # 1. Load Secrets
    rpc_url = get_secret(None, "BASE_RPC_URL") or "https://sepolia.base.org"
    private_key = get_secret(None, "BASE_PRIVATE_KEY") or get_secret(None, "SEPOLIA_PRIVATE_KEY")

    if not private_key:
        print("[!] Error: No private key found in secrets.")
        sys.exit(1)

    # Load deployed contract metadata
    deployment_file = Path("C:/RegimeOS/contracts/deployments/base_sepolia_deployment.json")
    if not deployment_file.exists():
        print("[!] Error: No deployment metadata found. Please deploy first.")
        sys.exit(1)

    with open(deployment_file, "r") as f:
        meta = json.load(f)
    contract_address = meta["contract_address"]
    print(f"[+] Loaded Deployed Contract Address: {contract_address}")

    # 2. Compile contract to get ABI
    contract_path = Path("C:/RegimeOS/contracts/SovereignVaultVaaS.sol")
    print(f"[*] Compiling contract to load ABI: {contract_path}...")
    try:
        try:
            solcx.install_solc("0.8.19")
        except Exception:
            pass
        solcx.set_solc_version("0.8.19")
        compiled = solcx.compile_files([str(contract_path)], output_values=["abi"])
        contract_key = "C:/RegimeOS/contracts/SovereignVaultVaaS.sol:SovereignVault"
        if contract_key not in compiled:
            contract_key = [k for k in compiled.keys() if "SovereignVault" in k][0]
        abi = compiled[contract_key]["abi"]
        print("[+] Compiled ABI loaded successfully.")
    except Exception as e:
        print(f"[!] Compilation failed: {e}")
        sys.exit(1)

    # 3. Instantiate Muji Arbiter
    print("[*] Initializing Muji Web3 Arbiter...")
    try:
        arbiter = MujiWeb3Arbiter(
            rpc_url=rpc_url,
            private_key=private_key,
            contract_address=contract_address,
            abi=abi
        )
        print("[+] Arbiter initialized and connected to blockchain.")
    except Exception as e:
        print(f"[!] Arbiter instantiation failed: {e}")
        sys.exit(1)

    # 4. Perform Anchor State Test
    import time
    task_id = os.getenv('TEST_RUN_ID')
    if not task_id:
        task_id = f"test-run-{int(time.time())}"

    # Payload checksum must be a 64-character lowercase hex string
    payload_checksum = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    consensus_class = "ARMADA_XVII_STABILITY_LOCK"

    print(f"[*] Submitting anchor transaction:")
    print(f"    - Task ID: {task_id}")
    print(f"    - Checksum: {payload_checksum}")
    print(f"    - Consensus Class: {consensus_class}")

    result = arbiter.anchor_state(task_id, payload_checksum, consensus_class)
    print("=" * 80)
    print("                     STATE ANCHOR EXECUTION RESULT")
    print("=" * 80)
    print(json.dumps(result, indent=4))
    print("=" * 80)

    if result.get("status") == "completed":
        print("[+] SUCCESS: Anchor state accepted and verified on-chain.")
        sys.exit(0)
    else:
        print("[!] FAILURE: Anchor state was not confirmed or reverted.")
        sys.exit(1)

if __name__ == "__main__":
    main()
