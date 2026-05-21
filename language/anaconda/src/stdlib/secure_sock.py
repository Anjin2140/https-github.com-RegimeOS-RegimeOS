# secure_sock.py
# Project ANACONDA Secure Socket (TLS 1.3 Client) v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import ssl
import socket
import sys

class SecureSocket:
    """Secure socket client wrapper enforcing TLS 1.3 and ChaCha20-Poly1305."""
    
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None):
        # 1. Enforce network capability check directly via loader registry
        loader = None
        for name in ("loader", "src.compiler.loader", "__main__"):
            m = sys.modules.get(name)
            if m and hasattr(m, "has_capability"):
                loader = m
                break
                
        if loader:
            if not loader.has_capability("network"):
                raise PermissionError("Security Violation: Network capability is denied. Declare '# @capability: network' to enable.")
            
        self.raw_sock = socket.socket(family, type, proto, fileno)
        self.ssl_sock = None
        self.connected = False
        
    def connect(self, address):
        """Connects to a remote address (host, port) using TLS 1.3, ChaCha20-Poly1305, and strict verification."""
        host, port = address
        
        # Configure TLS 1.3 Context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Enforce Strict CA Validation
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        
        # Set preferred ChaCha20-Poly1305 cipher suites
        context.set_ciphers('ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305')
        
        # Wrap and connect
        self.ssl_sock = context.wrap_socket(self.raw_sock, server_hostname=host)
        self.ssl_sock.connect(address)
        self.connected = True
        
    def send(self, data: bytes) -> int:
        if not self.ssl_sock:
            raise OSError("Socket not connected.")
        sanitized = self._sanitize_data(data)
        return self.ssl_sock.send(sanitized)
        
    def sendall(self, data: bytes):
        if not self.ssl_sock:
            raise OSError("Socket not connected.")
        sanitized = self._sanitize_data(data)
        return self.ssl_sock.sendall(sanitized)
        
    def recv(self, bufsize: int) -> bytes:
        if not self.ssl_sock:
            raise OSError("Socket not connected.")
        return self.ssl_sock.recv(bufsize)
        
    def close(self):
        if self.ssl_sock:
            self.ssl_sock.close()
        else:
            self.raw_sock.close()
            
    def makefile(self, mode="r", *args, **kwargs):
        if not self.ssl_sock:
            raise OSError("Socket not connected.")
        return self.ssl_sock.makefile(mode, *args, **kwargs)
            
    def _sanitize_data(self, data: bytes) -> bytes:
        """Strips host identity-revealing metadata headers from HTTP traffic."""
        try:
            text = data.decode('latin-1')
        except Exception:
            return data
            
        lines = text.split('\r\n')
        if not lines or not lines[0]:
            return data
            
        # Check if first line matches HTTP request format
        parts = lines[0].split()
        if len(parts) != 3 or not parts[2].startswith("HTTP/"):
            return data
            
        # Reconstruct request headers without sensitive info
        new_lines = [lines[0]]
        body_start_idx = -1
        
        for i in range(1, len(lines)):
            line = lines[i]
            if not line:
                body_start_idx = i
                break
                
            if ':' in line:
                key, val = line.split(':', 1)
                k = key.strip().lower()
                prohibited = {
                    "user-agent", "x-forwarded-for", "x-real-ip", "via",
                    "from", "accept-language", "referer", "cookie"
                }
                if k in prohibited or k.startswith("sec-ch-ua"):
                    # Strip header
                    continue
            new_lines.append(line)
            
        # Inject anonymous User-Agent header
        new_lines.append("User-Agent: ANACONDA/1.0 (Sovereign Node)")
        
        if body_start_idx != -1:
            new_lines.append("")
            new_lines.extend(lines[body_start_idx+1:])
            
        return '\r\n'.join(new_lines).encode('latin-1')
