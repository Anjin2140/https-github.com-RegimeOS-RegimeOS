import os

# Local .env support for production operations on Windows/Layer 2
env_path = "C:/RegimeOS/.env"
loaded_from_env_file = set()

if os.path.exists(env_path):
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v
                    loaded_from_env_file.add(k)
    except Exception as e:
        print(f"[*] Warning: Could not read local .env file: {e}")

try:
    from google.cloud import secretmanager
    HAS_GCP_SECRETS = True
except ImportError:
    HAS_GCP_SECRETS = False

def get_secret(project_id: str, name: str, version: str = "latest") -> str:
    """
    Production loader using Google Cloud Secret Manager.
    Falls back to environment variables or Colab userdata.
    """
    # 1. First priority: Environment Variables
    env_val = os.getenv(name)
    if env_val:
        if name in loaded_from_env_file and ("PRIVATE_KEY" in name or "SECRET" in name):
            print(f"[!] SECURITY WARNING: Sensitive key '{name}' is loaded from a flat-file (.env).")
            print("    For production mainnet security, set this as a system-level environment variable instead.")
        return env_val
    if name == "SEPOLIA_PRIVATE_KEY" and os.getenv("Ethereum_Private_Key"):
        return os.getenv("Ethereum_Private_Key")
    if name == "ALCHEMY_RPC_URL" and os.getenv("ALCHEMY_ETH_SEPOLIA_URL"):
        return os.getenv("ALCHEMY_ETH_SEPOLIA_URL")

    # 2. Second priority: GCP Secret Manager
    if HAS_GCP_SECRETS and project_id:
        try:
            client = secretmanager.SecretManagerServiceClient()
            path = f"projects/{project_id}/secrets/{name}/versions/{version}"
            response = client.access_secret_version(request={"name": path})
            return response.payload.data.decode("utf-8")
        except Exception as e:
            print(f"[!] GCP Secret Manager failed: {e}. Falling back to Colab Vault.")

    # 3. Third priority: Colab Vault fallback
    try:
        from google.colab import userdata
        # Map GCP secret names to Colab secret names if necessary
        if name == "SEPOLIA_PRIVATE_KEY":
            colab_name = "Ethereum_Private_Key"
        elif name == "ALCHEMY_RPC_URL":
            colab_name = "ALCHEMY_ETH_SEPOLIA_URL"
        else:
            colab_name = name
        return userdata.get(colab_name)
    except (ImportError, ModuleNotFoundError):
        return None
    except Exception as e:
        return None


if __name__ == "__main__":
    # Quick diagnostic
    rpc = get_secret(None, "ALCHEMY_RPC_URL")
    print(
f"[+] Secret Loader Initialized. Alchemy RPC loaded: {rpc.startswith('http') if rpc else False}")
