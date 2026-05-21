# loader.py
# Project ANACONDA Loader (Bootstrap Signature Verifier) v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import sys
import os
import inspect
import importlib.abc
import builtins

try:
    from src.compiler.vault import verify_air_signature, verify_vault_integrity
except ImportError:
    sys.path.insert(0, r"C:\RegimeOS\language\anaconda")
    from src.compiler.vault import verify_air_signature, verify_vault_integrity

# Global capability set populated during bootstrap
enabled_caps = set()

def has_capability(cap_name: str) -> bool:
    """Read-only capability checker accessed by stdlib modules."""
    return cap_name in enabled_caps

# 1. Custom Meta Path Finder for Capability Sandbox
class AnacondaMetaFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        name_root = fullname.split('.')[0]
        
        # Traverse stack to find the first non-internal importer module
        frame = inspect.currentframe().f_back
        importer_module = None
        while frame:
            mod_name = frame.f_globals.get("__name__")
            if mod_name and not mod_name.startswith("importlib") and mod_name not in ("_bootstrap", "_bootstrap_external"):
                importer_module = mod_name
                break
            frame = frame.f_back
            
        if importer_module == "__anaconda_secure__":
            # Block raw network libraries
            prohibited_network = {"socket", "urllib", "requests", "http", "aiohttp", "pika", "ftplib", "smtplib"}
            if name_root in prohibited_network:
                raise PermissionError(f"Security Violation: Import of '{fullname}' is restricted under Sovereign Sandbox Rules. Use 'secure_sock' instead.")
            
            # Block direct access to security modules
            prohibited_system = {"loader", "vault", "src.compiler.loader", "src.compiler.vault"}
            if fullname in prohibited_system or name_root in prohibited_system:
                raise PermissionError(f"Security Violation: Access to system module '{fullname}' is denied.")
            
            # Filesystem modules restriction
            fs_modules = {"os", "pathlib", "shutil", "io"}
            if name_root in fs_modules:
                if "filesystem" not in enabled_caps:
                    raise PermissionError(f"Security Violation: Filesystem access is denied for module '{fullname}'. Declare '# @capability: filesystem' to enable.")
                    
        return None

# 2. Protected list for sys.meta_path to prevent runtime bypass
class ProtectedMetaPath(list):
    def insert(self, index, object):
        if not isinstance(object, AnacondaMetaFinder):
            raise PermissionError("Security Violation: Modification of sys.meta_path is restricted.")
        super().insert(index, object)
        
    def remove(self, value):
        if isinstance(value, AnacondaMetaFinder):
            raise PermissionError("Security Violation: Cannot remove ANACONDA security finder.")
        super().remove(value)
        
    def pop(self, index=-1):
        item = self[index]
        if isinstance(item, AnacondaMetaFinder):
            raise PermissionError("Security Violation: Cannot remove ANACONDA security finder.")
        return super().pop(index)
        
    def clear(self):
        raise PermissionError("Security Violation: Cannot clear sys.meta_path.")
        
    def __delitem__(self, key):
        item = self[key]
        if isinstance(item, AnacondaMetaFinder):
            raise PermissionError("Security Violation: Cannot delete ANACONDA security finder.")
        super().__delitem__(key)
        
    def __setitem__(self, key, value):
        raise PermissionError("Security Violation: Cannot modify sys.meta_path directly.")

def parse_capabilities(script_path: str) -> set[str]:
    enabled = set()
    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# @capability:"):
                cap = line.split(":", 1)[1].strip().lower()
                enabled.add(cap)
            elif line.startswith("#") or not line:
                continue
            else:
                break
    return enabled

def main():
    global enabled_caps
    if len(sys.argv) < 2:
        print("Usage: python loader.py <script.air> [args...]")
        sys.exit(1)
        
    script_path = sys.argv[1]
    if not os.path.exists(script_path):
        print(f"[!] Executable not found: {script_path}")
        sys.exit(1)
        
    # In-memory Vault integrity verification
    if not verify_vault_integrity():
        print("ANACONDA_SECURITY_VIOLATION: Vault integrity compromised.")
        sys.exit(99)
        
    # Verify the Ed25519 signature of the target script
    if not verify_air_signature(script_path):
        print("EXIT_CODE_SECURITY_VIOLATION")
        sys.exit(99)
        
    # Parse and set Capabilities
    enabled_caps.clear()
    enabled_caps.update(parse_capabilities(script_path))
    
    # Install Meta Path Finder & Protect sys.meta_path
    sys.meta_path.insert(0, AnacondaMetaFinder())
    sys.meta_path = ProtectedMetaPath(sys.meta_path)
    
    # Hook builtin open for filesystem check
    original_open = builtins.open
    
    def secure_open(file, mode='r', *args, **kwargs):
        # Inspect stack to see if we are in the user script
        frame = inspect.currentframe().f_back
        in_user_script = False
        while frame:
            if frame.f_globals.get("__name__") == "__anaconda_secure__":
                in_user_script = True
                break
            frame = frame.f_back
            
        if in_user_script:
            if "filesystem" not in enabled_caps:
                raise PermissionError("Security Violation: Filesystem access is denied. Declare '# @capability: filesystem' to enable.")
                
        return original_open(file, mode, *args, **kwargs)
        
    builtins.open = secure_open
    
    # Expose the correct script arguments to sys.argv
    sys.argv = sys.argv[1:]
    
    # Read script bytecode
    with open(script_path, "r", encoding="utf-8") as f:
        code_content = f.read()
        
    global_ns = {
        "__name__": "__anaconda_secure__",
        "__file__": os.path.abspath(script_path),
        "__builtins__": builtins,
    }
    
    try:
        # Run bytecode in isolated environment
        exec(code_content, global_ns)
    except SystemExit as se:
        sys.exit(se.code)
    except PermissionError as pe:
        # Clean generic security violations to prevent path leaks
        msg = str(pe)
        msg = msg.replace("C:\\RegimeOS", "RegimeOS")
        msg = msg.replace(os.path.abspath(script_path), os.path.basename(script_path))
        print(f"ANACONDA_SECURITY_VIOLATION: {msg}")
        sys.exit(99)
    except Exception as e:
        err_msg = str(e)
        err_msg = err_msg.replace("C:\\RegimeOS", "RegimeOS")
        err_msg = err_msg.replace(os.path.abspath(script_path), os.path.basename(script_path))
        print(f"Runtime Execution Error: {err_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
