# ANACONDA Language Syntax & Grammar Specification v1.0

This document defines the formal grammar rules, keywords, types, and mathematical operations of the **ANACONDA** programming language environment.

---

## 1. File Formats & Extensions

*   **`.ana`**: ANACONDA high-level source files.
*   **`.air`**: ANACONDA Intermediate Representation. These are transpiled Python files appended with a cryptographic Ed25519 signature payload.

---

## 2. Core Type System

ANACONDA enforces a strict mathematical and logical sandbox:

| High-level Type | Native Runtime Class | Description |
| :--- | :--- | :--- |
| `regime` | `RegimeDecimal` | Base-65536 arbitrary-precision fixed-point number. Zero drift. |
| `ternary` | `Ternary` | 3-state logical type: `-1` (False), `0` (Unknown), `1` (True). |
| `hahn` | `HahnDecimal` | Non-Archimedean dual numbers containing a real part and an infinitesimal coefficient ($a + b\epsilon$). |

---

## 3. Literals & Constants

ANACONDA transpiles source literals directly at parse time to prevent floating-point entropy leak:

### 3.1. Numeric Constants
*   **Integers**: Represented as standard integers.
*   **Decimal/Float Literals** (e.g., `3.14159`): Automatically transformed at compile time to `RegimeDecimal.from_str("3.14159")`.

### 3.2. Ternary Logic Constants
ANACONDA introduces three logic constants replacing native boolean values:
*   `TRUE`: Resolves to `Ternary(1)`
*   `FALSE`: Resolves to `Ternary(-1)`
*   `UNKNOWN` or `PARADOX`: Resolves to `Ternary(0)` (replaces `None` or deadband states in boolean evaluations).

### 3.3. Infinitesimal Constant
*   `epsilon` or `eps`: Resolves to `HahnDecimal(RegimeDecimal.One, 1)`. Operates under $1 + \epsilon > 1$.

---

## 4. Operator Mappings

### 4.1. Arithmetic Operators
Arithmetic operations (`+`, `-`, `*`, `/`) between `regime` and `hahn` types are supported:
*   `regime + regime -> regime`
*   `regime + hahn -> hahn`
*   `hahn + regime -> hahn`
*   `hahn + hahn -> hahn`

### 4.2. Ternary Logic Operators
Logical operations are executed using bitwise operators to avoid short-circuiting drift:
*   `a & b`: Ternary AND. Operates with Paradox Handling: `TRUE & FALSE -> UNKNOWN`.
*   `a | b`: Ternary OR.
*   `~a`: Ternary NOT.
*   `a ^ b`: Ternary XOR.

---

## 5. Security & Validation Rules

1.  **Strict Lumber Checking**: Code compilation under `--strict-lumber` systematically rejects statements invoking `eval()`, `exec()`, or import instructions targeting `importlib`, network modules (`requests`, `urllib`), and OS sockets.
2.  **Code Signing Verification**: Output `.air` files are strictly required to possess a valid Ed25519 signature payload in a trailing comment. Direct execution of `.air` files requires loading via `loader.py` or the secure runtime to verify authenticity.
3.  **Compile-time Promotion Warnings**: Implicit promotion of native float literals or coercion of types triggers a explicit compilation warning indicating line, column, and variable context.

---

## 6. Capability Sandbox & Permissions

ANACONDA enforces a **Default Deny All** capability sandbox at runtime. Every script must declare its required permissions using comment annotations at the top of the file:

```python
# @capability: filesystem
# @capability: network
```

*   **`filesystem`**: Allows file reads and writes using the builtin `open()` function, and importing of standard filesystem modules (`os`, `pathlib`, `shutil`, `io`). Without this, any access attempts raise a `PermissionError`.
*   **`network`**: Allows importing and connecting using the `secure_sock` standard library. Raw python network modules (e.g., `socket`, `urllib`, `requests`, etc.) are unconditionally blocked in all environments.

---

## 7. Standard Library Modules

### 7.1. Secure Socket (`secure_sock`)
The `SecureSocket` class enforces TLS 1.3, strict CA validation, and ChaCha20-Poly1305. It also automatically strips identity-revealing metadata headers from HTTP traffic.

*   `SecureSocket()`: Constructor. Verifies `network` capability.
*   `connect((host, port))`: Establishes secure connection.
*   `send(data: bytes) -> int`: Sends sanitized bytes.
*   `sendall(data: bytes)`: Sends all sanitized bytes.
*   `recv(bufsize: int) -> bytes`: Receives bytes.
*   `close()`: Closes socket connection.

### 7.2. Sovereign Identity (`sovereign_id`)
Manages the cryptographic Ed25519 identity of the local node. Key custody is offloaded to the Windows Credential Manager under the `ANACONDA_Sovereign_ID` service using the `keyring` API.

*   `get_public_key_bytes() -> bytes`: Returns 32-byte raw public key.
*   `sign_data(data: bytes) -> bytes`: Signs message with private key.
*   `verify_signature(pub_bytes: bytes, signature: bytes, data: bytes) -> bool`: Verifies signature.

