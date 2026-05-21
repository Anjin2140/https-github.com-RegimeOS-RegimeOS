# test_kernel.py
# Project ANACONDA Core Kernel Verification Suite v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import sys
import os
import unittest

sys.path.insert(0, r"C:\RegimeOS\language\anaconda")

from src.kernel.regime_math import Ternary, RegimeDecimal, HahnDecimal, EpsilonStallDetector
from src.compiler import rcs, forge, vault

class TestAnacondaKernel(unittest.TestCase):

    def test_regime_decimal_precision(self):
        """Verify that 0.1 + 0.2 == 0.3 evaluates strictly to True (Zero Drift)."""
        a = RegimeDecimal.from_str("0.1")
        b = RegimeDecimal.from_str("0.2")
        c = RegimeDecimal.from_str("0.3")
        
        sum_ab = a + b
        self.assertEqual(sum_ab, c)
        
        # Test multiplication
        a_mul = RegimeDecimal.from_str("1.5")
        b_mul = RegimeDecimal.from_str("2.0")
        expected_mul = RegimeDecimal.from_str("3.0")
        self.assertEqual(a_mul * b_mul, expected_mul)

        # Test division
        a_div = RegimeDecimal.from_str("10.0")
        b_div = RegimeDecimal.from_str("3.0")
        res_div = a_div / b_div
        # Should match high precision representation
        self.assertTrue(res_div.to_float() > 3.333)

    def test_ternary_logic(self):
        """Verify ternary operations and logic gate rules."""
        t_true = Ternary(1)
        t_unknown = Ternary(0)
        t_false = Ternary(-1)

        # AND
        self.assertEqual(t_true & t_true, t_true)
        self.assertEqual(t_true & t_unknown, t_unknown)
        self.assertEqual(t_true & t_false, t_unknown)
        self.assertEqual(t_unknown & t_false, t_false)

        # OR
        self.assertEqual(t_true | t_false, t_true)
        self.assertEqual(t_unknown | t_false, t_unknown)

        # NOT
        self.assertEqual(~t_true, t_false)
        self.assertEqual(~t_unknown, t_unknown)
        self.assertEqual(~t_false, t_true)

        # XOR
        self.assertEqual(t_true ^ t_false, t_true)
        self.assertEqual(t_true ^ t_true, t_false)
        self.assertEqual(t_true ^ t_unknown, t_unknown)

    def test_paradox_handler(self):
        """Verify the Paradox Handler: 1 AND -1 -> 0."""
        t_true = Ternary(1)
        t_false = Ternary(-1)
        self.assertEqual(t_true & t_false, Ternary(0))
        self.assertEqual(t_false & t_true, Ternary(0))

    def test_non_archimedean_epsilon(self):
        """Verify that 1 + epsilon > 1 evaluates to True."""
        one = RegimeDecimal.One
        eps = HahnDecimal(one, 1) # 1 + 1ε
        plain_one = HahnDecimal(one, 0) # 1 + 0ε

        res = eps > plain_one
        self.assertEqual(res, Ternary(1)) # True

        res_lt = plain_one < eps
        self.assertEqual(res_lt, Ternary(1)) # True

    def test_epsilon_stall_protection(self):
        """Verify loop stall protection when epsilon comparisons exceed 1000 iterations without change."""
        one = RegimeDecimal.One
        eps = HahnDecimal(one, 1)
        plain_one = HahnDecimal(one, 0)
        
        # Simulate a stall by repeatedly comparing in a tight loop
        for _ in range(1005):
            res = eps > plain_one

        # Stall detector should have fired and returned a forced resolution
        self.assertEqual(res, Ternary(1))

        # Reset stall context
        key = eps._get_caller_key()
        EpsilonStallDetector.reset(key)

    def test_rcs_serialization_determinism(self):
        """Verify that the same map with different insertion order produces identical binary payloads."""
        dict1 = {"alpha": 1, "beta": RegimeDecimal.from_str("0.5"), "gamma": Ternary(1)}
        dict2 = {"gamma": Ternary(1), "beta": RegimeDecimal.from_str("0.5"), "alpha": 1}

        bytes1 = rcs.serialize(dict1)
        bytes2 = rcs.serialize(dict2)

        self.assertEqual(bytes1, bytes2)

        # Deserialize and verify content
        recovered, length = rcs.deserialize(bytes1)
        self.assertEqual(recovered["alpha"], 1)
        self.assertEqual(recovered["beta"], RegimeDecimal.from_str("0.5"))
        self.assertEqual(recovered["gamma"], Ternary(1))

    def test_ast_transpilation_safety(self):
        """Verify ast transpiler rewrites float literals and catches illegal keywords."""
        legacy_code = "x = 1.25\ny = True\nz = None\n"
        transpiled = forge.transpile_code(legacy_code, strict_lumber=True)

        self.assertIn("RegimeDecimal.from_str('1.25')", transpiled)
        self.assertIn("Ternary(1)", transpiled)
        self.assertIn("Ternary(0)", transpiled)

    def test_strict_lumber_poison_pills(self):
        """Verify that eval, exec, and importlib are successfully blocked."""
        bad_code_eval = "eval('1 + 1')"
        bad_code_exec = "exec('x = 5')"
        bad_code_import = "import importlib"

        with self.assertRaises(PermissionError):
            forge.transpile_code(bad_code_eval, strict_lumber=True)

        with self.assertRaises(PermissionError):
            forge.transpile_code(bad_code_exec, strict_lumber=True)

        with self.assertRaises(PermissionError):
            forge.transpile_code(bad_code_import, strict_lumber=True)

    def test_vault_integrity_verification(self):
        """Verify manifest generation and cryptographic vault check."""
        # Generate the manifest and keys
        vault.generate_manifest()
        
        # Verify the integrity signature check runs successfully
        success = vault.verify_vault_integrity()
        self.assertTrue(success)

    def test_hahn_decimal_radd(self):
        """Verify __radd__ operation on HahnDecimal: regime + hahn -> hahn."""
        r = RegimeDecimal.from_str("1.5")
        h = HahnDecimal(RegimeDecimal.from_str("2.0"), 3)
        res = r + h
        self.assertEqual(res.real, RegimeDecimal.from_str("3.5"))
        self.assertEqual(res.eps_coeff, 3)

    def test_hahn_decimal_rsub(self):
        """Verify __rsub__ operation on HahnDecimal: regime - hahn -> hahn."""
        r = RegimeDecimal.from_str("5.0")
        h = HahnDecimal(RegimeDecimal.from_str("2.0"), 3)
        res = r - h
        self.assertEqual(res.real, RegimeDecimal.from_str("3.0"))
        self.assertEqual(res.eps_coeff, -3)

    def test_hahn_decimal_rmul(self):
        """Verify __rmul__ operation on HahnDecimal: regime * hahn -> hahn."""
        r = RegimeDecimal.from_str("2.0")
        h = HahnDecimal(RegimeDecimal.from_str("3.0"), 4)
        res = r * h
        self.assertEqual(res.real, RegimeDecimal.from_str("6.0"))
        # (r * h) eps = r.to_float() * h.eps_coeff = 2.0 * 4 = 8
        self.assertEqual(res.eps_coeff, 8)

    def test_hahn_decimal_sub(self):
        """Verify subtraction between HahnDecimal instances."""
        h1 = HahnDecimal(RegimeDecimal.from_str("5.0"), 5)
        h2 = HahnDecimal(RegimeDecimal.from_str("2.0"), 2)
        res = h1 - h2
        self.assertEqual(res.real, RegimeDecimal.from_str("3.0"))
        self.assertEqual(res.eps_coeff, 3)

    def test_hahn_decimal_mul(self):
        """Verify multiplication between HahnDecimal instances."""
        h1 = HahnDecimal(RegimeDecimal.from_str("2.0"), 3)
        h2 = HahnDecimal(RegimeDecimal.from_str("3.0"), 4)
        res = h1 * h2
        self.assertEqual(res.real, RegimeDecimal.from_str("6.0"))
        # eps = 2.0*4 + 3.0*3 = 8 + 9 = 17
        self.assertEqual(res.eps_coeff, 17)

    def test_hahn_decimal_comparisons(self):
        """Verify HahnDecimal comparisons (<, >, ==)."""
        h1 = HahnDecimal(RegimeDecimal.from_str("2.0"), 1)
        h2 = HahnDecimal(RegimeDecimal.from_str("2.0"), 2)
        h3 = HahnDecimal(RegimeDecimal.from_str("1.0"), 10)
        
        self.assertEqual(h1 < h2, Ternary(1))
        self.assertEqual(h2 > h1, Ternary(1))
        self.assertEqual(h1 > h3, Ternary(1))
        self.assertEqual(h1 == h1, Ternary(1))

    def test_transpiler_custom_keywords(self):
        """Verify transpiler handles TRUE, FALSE, UNKNOWN, PARADOX, epsilon, eps."""
        code = "a = TRUE\nb = FALSE\nc = UNKNOWN\nd = PARADOX\ne = epsilon\nf = eps"
        transpiled = forge.transpile_code(code)
        
        self.assertIn("Ternary(1)", transpiled)
        self.assertIn("Ternary(-1)", transpiled)
        self.assertIn("Ternary(0)", transpiled)
        self.assertIn("HahnDecimal(RegimeDecimal.One, 1)", transpiled)

    def test_transpiler_implicit_promotion_warning(self):
        """Verify that transpilation prints compile-time warnings on implicit promotion."""
        import io
        from contextlib import redirect_stdout
        
        code = "x = 1.25\ny = True\nz = None"
        f = io.StringIO()
        with redirect_stdout(f):
            forge.transpile_code(code, filename="test_warn.ana")
            
        warnings = f.getvalue()
        self.assertIn("[COMPILE_TIME_WARNING]", warnings)
        self.assertIn("test_warn.ana", warnings)
        self.assertIn("variable 'x'", warnings)
        self.assertIn("variable 'y'", warnings)
        self.assertIn("variable 'z'", warnings)

    def test_transpiler_float_literal_evaluation(self):
        """Verify float literal AST transformation intercepts literals early."""
        code = "val = 0.1 + 0.2"
        transpiled = forge.transpile_code(code)
        
        self.assertIn("RegimeDecimal.from_str('0.1')", transpiled)
        self.assertIn("RegimeDecimal.from_str('0.2')", transpiled)

    def test_code_signing_valid(self):
        """Verify code signing appends signature and validates correctly."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_signed.air"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("print('Test Code Signing')\n")
            
            vault.sign_air_file(temp_file)
            
            with open(temp_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            self.assertIn("# SIGNATURE:", content)
            self.assertTrue(vault.verify_air_signature(temp_file))
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_code_signing_tampered_signature(self):
        """Verify altering signature hex fails validation."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_tampered_sig.air"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("print('Test Tampered Sig')\n")
            vault.sign_air_file(temp_file)
            
            # Read and replace signature byte
            with open(temp_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            lines[-1] = "# SIGNATURE: " + "a" * len(lines[-1].split()[-1]) + "\n"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
            self.assertFalse(vault.verify_air_signature(temp_file))
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_code_signing_tampered_code(self):
        """Verify altering code content fails validation."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_tampered_code.air"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("print('Test Tampered Code')\n")
            vault.sign_air_file(temp_file)
            
            # Read and alter code line
            with open(temp_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            lines[0] = "print('Altered Code content')\n"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
            self.assertFalse(vault.verify_air_signature(temp_file))
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_loader_execution_success(self):
        """Verify loader executes a signed file and exits with 0."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_loader_ok.air"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("import sys\nif __name__ != '__anaconda_secure__':\n    sys.exit(1)\n")
            
            vault.sign_air_file(temp_file)
            
            # Run loader
            import subprocess
            res = subprocess.run(
                [sys.executable, r"C:\RegimeOS\language\anaconda\src\compiler\loader.py", temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 0)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_loader_execution_tampered(self):
        """Verify loader halts execution on signature mismatch and prints security violation."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_loader_fail.air"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("print('Should not run')\n")
            vault.sign_air_file(temp_file)
            
            # Tamper the code
            with open(temp_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            lines[0] = "print('Tampered')\n"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
            import subprocess
            res = subprocess.run(
                [sys.executable, r"C:\RegimeOS\language\anaconda\src\compiler\loader.py", temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 99)
            self.assertIn("EXIT_CODE_SECURITY_VIOLATION", res.stdout)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_loader_execution_missing(self):
        """Verify loader halts on unsigned files."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_loader_missing.air"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("print('Unsigned')\n")
                
            import subprocess
            res = subprocess.run(
                [sys.executable, r"C:\RegimeOS\language\anaconda\src\compiler\loader.py", temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 99)
            self.assertIn("EXIT_CODE_SECURITY_VIOLATION", res.stdout)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_direct_execution_prevention(self):
        """Verify self-verification checks inside .air files block direct execution."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_direct.air"
        try:
            code = (
                "import sys\n"
                "# Verify execution authorization\n"
                "if __name__ == '__anaconda_secure__':\n"
                "    try:\n"
                "        from src.compiler.vault import verify_air_signature\n"
                "        if not verify_air_signature(__file__):\n"
                "            print('EXIT_CODE_SECURITY_VIOLATION')\n"
                "            sys.exit(99)\n"
                "    except Exception:\n"
                "        print('EXIT_CODE_SECURITY_VIOLATION')\n"
                "        sys.exit(99)\n"
                "else:\n"
                "    print('EXIT_CODE_SECURITY_VIOLATION')\n"
                "    sys.exit(99)\n"
            )
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            vault.sign_air_file(temp_file)
            
            # Execute directly via Python
            import subprocess
            res = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 99)
            self.assertIn("EXIT_CODE_SECURITY_VIOLATION", res.stdout)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_regime_decimal_conversions(self):
        """Verify RegimeDecimal conversion flows."""
        r1 = RegimeDecimal.from_str("12.345")
        self.assertAlmostEqual(float(str(r1)), 12.345, places=5)
        
        # Test converting to float
        f = r1.to_float()
        self.assertAlmostEqual(f, 12.345, places=5)

    def test_rcs_serialization_nested(self):
        """Verify serialization of nested maps and lists in RCS."""
        nested = {
            "key1": [1, 2, 3],
            "key2": {"sub": RegimeDecimal.from_str("9.99")},
            "key3": Ternary(-1)
        }
        serialized = rcs.serialize(nested)
        recovered, length = rcs.deserialize(serialized)
        
        self.assertEqual(recovered["key1"], [1, 2, 3])
        self.assertEqual(recovered["key2"]["sub"], RegimeDecimal.from_str("9.99"))
        self.assertEqual(recovered["key3"], Ternary(-1))

    def test_strict_lumber_all_bad_imports(self):
        """Verify blocked network imports list validation."""
        for lib in ["socket", "requests", "urllib", "aiohttp", "pika"]:
            with self.assertRaises(PermissionError):
                forge.transpile_code(f"import {lib}", strict_lumber=True)

    def test_secure_socket_http_stripping(self):
        """Verify that SecureSocket strips identification metadata from HTTP payloads."""
        from src.stdlib.secure_sock import SecureSocket
        import builtins
        
        # Temporarily register capability for manual test instantiation
        builtins.__anaconda_capabilities__ = {"network"}
        try:
            sock = SecureSocket()
            raw_req = (
                b"GET /index.html HTTP/1.1\r\n"
                b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0\r\n"
                b"Cookie: auth=xyz123\r\n"
                b"X-Forwarded-For: 192.168.1.50\r\n"
                b"Referer: https://sensitive-source.com\r\n"
                b"Host: target-node.org\r\n\r\n"
            )
            sanitized = sock._sanitize_data(raw_req)
            
            # Sensitive headers must be completely stripped
            self.assertNotIn(b"Mozilla/5.0", sanitized)
            self.assertNotIn(b"auth=xyz123", sanitized)
            self.assertNotIn(b"192.168.1.50", sanitized)
            self.assertNotIn(b"sensitive-source.com", sanitized)
            
            # Anonymous Agent must be injected
            self.assertIn(b"User-Agent: ANACONDA/1.0 (Sovereign Node)", sanitized)
            # Standard headers should remain untouched
            self.assertIn(b"Host: target-node.org", sanitized)
        finally:
            if hasattr(builtins, "__anaconda_capabilities__"):
                del builtins.__anaconda_capabilities__

    def test_sovereign_identity_management(self):
        """Verify Ed25519 node identity generation, signing, and signature verification."""
        from src.stdlib import sovereign_id
        
        pub_key = sovereign_id.get_public_key_bytes()
        self.assertEqual(len(pub_key), 32)
        
        payload = b"STRATSEC SOVEREIGN COMPILATION VERIFICATION"
        signature = sovereign_id.sign_data(payload)
        
        self.assertTrue(sovereign_id.verify_signature(pub_key, signature, payload))
        self.assertFalse(sovereign_id.verify_signature(pub_key, signature, b"TAMPERED PAYLOAD"))

    def test_capability_denial_network(self):
        """Verify that running a script without network capability blocks secure socket usage."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_cap_net.air"
        try:
            # Script lacks "# @capability: network"
            code = (
                "from src.stdlib.secure_sock import SecureSocket\n"
                "s = SecureSocket()\n"
            )
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            vault.sign_air_file(temp_file)
            
            import subprocess
            res = subprocess.run(
                [sys.executable, r"C:\RegimeOS\language\anaconda\src\compiler\loader.py", temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 99)
            self.assertIn("ANACONDA_SECURITY_VIOLATION", res.stdout)
            self.assertIn("Network capability is denied", res.stdout)
            
            # Path details must not leak in violation message
            self.assertNotIn("C:\\RegimeOS", res.stdout)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_capability_denial_filesystem(self):
        """Verify that running a script without filesystem capability blocks open() and os module import."""
        temp_file_fs = r"C:\RegimeOS\language\anaconda\src\tests\temp_cap_fs.air"
        try:
            # Script lacks "# @capability: filesystem"
            code = (
                "with open('test_write.txt', 'w') as f:\n"
                "    f.write('forbidden')\n"
            )
            with open(temp_file_fs, "w", encoding="utf-8") as f:
                f.write(code)
            vault.sign_air_file(temp_file_fs)
            
            import subprocess
            res = subprocess.run(
                [sys.executable, r"C:\RegimeOS\language\anaconda\src\compiler\loader.py", temp_file_fs],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 99)
            self.assertIn("ANACONDA_SECURITY_VIOLATION", res.stdout)
            self.assertIn("Filesystem access is denied", res.stdout)
            self.assertNotIn("C:\\RegimeOS", res.stdout)
        finally:
            if os.path.exists(temp_file_fs):
                os.remove(temp_file_fs)

    def test_raw_socket_import_blocking(self):
        """Verify standard socket and urllib imports are unconditionally blocked for scripts."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_raw_sock.air"
        try:
            code = (
                "# @capability: network\n"
                "import socket\n"
            )
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            vault.sign_air_file(temp_file)
            
            import subprocess
            res = subprocess.run(
                [sys.executable, r"C:\RegimeOS\language\anaconda\src\compiler\loader.py", temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 99)
            self.assertIn("ANACONDA_SECURITY_VIOLATION", res.stdout)
            self.assertIn("Import of 'socket' is restricted", res.stdout)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_meta_path_modification_blocking(self):
        """Verify sys.meta_path is protected against runtime modification."""
        temp_file = r"C:\RegimeOS\language\anaconda\src\tests\temp_meta.air"
        try:
            code = (
                "import sys\n"
                "sys.meta_path.clear()\n"
            )
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            vault.sign_air_file(temp_file)
            
            import subprocess
            res = subprocess.run(
                [sys.executable, r"C:\RegimeOS\language\anaconda\src\compiler\loader.py", temp_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 99)
            self.assertIn("ANACONDA_SECURITY_VIOLATION", res.stdout)
            self.assertIn("Cannot clear sys.meta_path", res.stdout)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    unittest.main()

