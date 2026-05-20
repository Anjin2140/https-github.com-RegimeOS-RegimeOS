# C:\RegimeOS\bin\deploy_vaas.py
# ==============================================================================
# Verification-as-a-Service (VaaS) Contract Deployer
# Product of Armada XVII | Owned & Operated by Christopher E. Adams
# ==============================================================================
import os
import sys
import json
from pathlib import Path
from web3 import Web3
from eth_account import Account
import solcx

# Fix import path for secret_manager
sys.path.insert(0, str(Path(__file__).parent.absolute()))
from secret_manager import get_secret

def main():
    print("=" * 80)
    print("           ARMADA XVII - SOVEREIGN VAULT VAAS LAYER 2 DEPLOYER")
    print("=" * 80)

    # 1. Load Secrets
    rpc_url = get_secret(None, "BASE_RPC_URL") or "https://sepolia.base.org"
    private_key = get_secret(None, "BASE_PRIVATE_KEY") or get_secret(None, "SEPOLIA_PRIVATE_KEY")

    if not private_key:
        print("[!] Warning: No BASE_PRIVATE_KEY or SEPOLIA_PRIVATE_KEY found in secrets.")
        print("[*] To deploy, please set the key in environment variables or create a local .env:")
        print("    File: C:\\RegimeOS\\.env")
        print("    Content:")
        print("        BASE_RPC_URL=https://sepolia.base.org")
        print("        BASE_PRIVATE_KEY=your_private_key_here")
        print("-" * 80)
        print("[*] Generating a temporary deployer account for dry-run/preview...")
        temp_acct = Account.create()
        print(f"    Temporary Address: {temp_acct.address}")
        print(f"    Temporary Private Key: {temp_acct.key.hex()}")
        print("[!] Run again after setting a funded private key to deploy.")
        sys.exit(0)

    # Clean private key format
    if private_key.startswith("0x"):
        private_key = private_key[2:]

    # 2. Connect to EVM Network
    print(f"[*] Connecting to RPC Endpoint: {rpc_url}...")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("[!] Connection Error: Failed to connect to RPC endpoint.")
        sys.exit(1)
    
    chain_id = w3.eth.chain_id
    print(f"[+] Connected successfully. Chain ID: {chain_id}")

    # 3. Setup Account
    deployer = Account.from_key(private_key)
    balance_wei = w3.eth.get_balance(deployer.address)
    balance_eth = w3.from_wei(balance_wei, "ether")
    print(f"[+] Deployer Address: {deployer.address}")
    print(f"[+] Account Balance: {balance_eth} ETH")

    if balance_wei == 0:
        print("[!] Warning: Account balance is 0. Cannot pay for gas.")
        print("[*] Please fund this account on Base Sepolia faucet or Mainnet before deploying.")
        sys.exit(0)

    # 4. Compile Contract
    contract_path = Path("C:/RegimeOS/contracts/SovereignVaultVaaS.sol")
    print(f"[*] Compiling contract: {contract_path}...")
    try:
        try:
            solcx.install_solc("0.8.19")
        except Exception:
            pass
        solcx.set_solc_version("0.8.19")
        compiled = solcx.compile_files([str(contract_path)], output_values=["abi", "bin"])
        
        contract_key = "C:/RegimeOS/contracts/SovereignVaultVaaS.sol:SovereignVault"
        if contract_key not in compiled:
            # Fallback path keys
            contract_key = [k for k in compiled.keys() if "SovereignVault" in k][0]
            
        abi = compiled[contract_key]["abi"]
        bytecode = compiled[contract_key]["bin"]
        print("[+] Compilation complete.")
    except Exception as e:
        print(f"[!] Compilation Error: {e}")
        sys.exit(1)

    # 5. Build Deployment Transaction
    # Constructor parameters: Initial Fee = 0.001 ETH (1e15 wei), Treasury = Configured Vault / Deployer Address
    initial_fee_wei = w3.to_wei(0.001, "ether")
    treasury_address = get_secret(None, "VAAS_TREASURY_ADDRESS") or deployer.address
    
    print(f"[*] Building deployment transaction...")
    print(f"    - Initial Toll Fee: {w3.from_wei(initial_fee_wei, 'ether')} ETH")
    print(f"    - Fee Treasury Address: {treasury_address}")

    SovereignVault = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    try:
        construct_tx = SovereignVault.constructor(initial_fee_wei, treasury_address).build_transaction({
            'from': deployer.address,
            'nonce': w3.eth.get_transaction_count(deployer.address),
            'gas': 1500000,
            'gasPrice': int(w3.eth.gas_price * 1.2)  # 20% Gas buffer
        })
        print(f"[+] Transaction built. Estimated Gas Cost: {construct_tx['gas']} units")
    except Exception as e:
        print(f"[!] Transaction building failed: {e}")
        sys.exit(1)

    # 6. Sign and Send
    print("[*] Signing transaction off-chain...")
    signed_tx = w3.eth.account.sign_transaction(construct_tx, private_key=deployer.key)
    
    print("[*] Broadcasting transaction to the network...")
    raw_tx = getattr(signed_tx, "rawTransaction", getattr(signed_tx, "raw_transaction", None))
    tx_hash = w3.eth.send_raw_transaction(raw_tx)
    print(f"[+] Broadcast successful. Tx Hash: {tx_hash.hex()}")
    print("[*] Waiting for transaction confirmation (receipt)...")
    
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        if receipt.status == 1:
            explorer_base = "https://sepolia.basescan.org" if chain_id in [8453, 84532] else "https://sepolia.etherscan.io"
            print("=" * 80)
            print("         CONTRACT DEPLOYED SUCCESSFULLY")
            print("=" * 80)
            print(f"Deployed Contract Address: {receipt.contractAddress}")
            print(f"Transaction Hash:          {tx_hash.hex()}")
            print(f"Block Number:              {receipt.blockNumber}")
            print(f"Gas Used:                  {receipt.gasUsed}")
            print(f"Explorer URL:              {explorer_base}/address/{receipt.contractAddress}")
            print("=" * 80)
            
            # Save the deployment artifact
            artifacts_dir = Path("C:/RegimeOS/contracts/deployments")
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            deployment_info = {
                "contract_address": receipt.contractAddress,
                "deployer": deployer.address,
                "treasury": treasury_address,
                "tx_hash": tx_hash.hex(),
                "chain_id": chain_id,
                "timestamp": receipt.blockNumber
            }
            with open(artifacts_dir / "base_sepolia_deployment.json", "w") as f:
                json.dump(deployment_info, f, indent=4)
            print(f"[+] Deployment metadata saved to C:\\RegimeOS\\contracts\\deployments\\base_sepolia_deployment.json")
        else:
            print("[!] Deployment Failed: Transaction reverted by EVM.")
            sys.exit(1)
    except Exception as e:
        print(f"[!] Deployment Timeout / Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
