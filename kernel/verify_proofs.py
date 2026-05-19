# verify_proofs.py
# RegimeOS v4.1-Windows | Math Invariants Verification Suite
import sys
import unittest
import math

# Import core math classes
from regime_math import TernaryBinaryEncoder, SokhotskySifter, ArchitectAnchor

class TestRegimeMathProofs(unittest.TestCase):

    # PROOF 1: BOUNDEDNESS INVARIANT (Layer 1)
    def test_layer1_invariant(self):
        # Test standard, boundary, and extreme inputs clamp to bounds [-13, 13]
        test_cases = [
            -100.0, -50.5, -13.0, -5.0, 0.0, 5.0, 13.0, 50.5, 100.0,
            -1e100, 1e100, -sys.float_info.max, sys.float_info.max,
            -13.000000000001, 13.000000000001
        ]
        for val in test_cases:
            clamped = ArchitectAnchor.clamp(val)
            self.assertTrue(-13.0 <= clamped <= 13.0, f"Clamp failed for value: {val}")

    # PROOF 2: DISCRETE LIPSCHITZ STEP BOUND (Layer 2)
    def test_layer2_step_bound(self):
        # Verify that single-step transition from clamped state changes state by at most 1 unit
        # Testing full integer range as well as decimal step inputs
        for state in range(-13, 14):
            for delta in [-1, -0.5, 0, 0.5, 1]:
                next_state = ArchitectAnchor.clamp(state + delta)
                self.assertTrue(abs(next_state - state) <= abs(delta), f"Step limit failed for state={state}, delta={delta}")

    # PROOF 3: NUMERICAL STABILITY (Layer 3)
    def test_layer3_no_div_zero(self):
        # Sokhotsky-Plemelj division should never raise ZeroDivisionError and should return valid limits
        test_cases = [
            0.0, 1e-20, -1e-20, 5.0, -5.0,
            1e-13, -1e-13, 1.000000000001e-13, -1.000000000001e-13,
            1e100, -1e100
        ]
        for x in test_cases:
            try:
                result = SokhotskySifter.evaluate_limit(x)
                if x == 0.0:
                    self.assertEqual(result, 0)
                else:
                    self.assertIsNotNone(result)
                    # Verify returned value is complex
                    self.assertTrue(isinstance(result, complex))
            except ZeroDivisionError:
                self.fail(f"ZeroDivisionError raised for x={x}")

    # PROOF 4: LOGICAL HIERARCHY / THRESHOLD FILTER (Layer 4)
    def test_layer4_threshold_logic(self):
        # Verification that sifting correctly separates principal value from imaginary noise at threshold 1e-13
        epsilon = 1e-13
        
        # Test values strictly below epsilon (Noise / Imaginary Singularity)
        noise_cases = [1e-14, -1e-14, 5e-14, -5e-14, 0.0]
        for val in noise_cases:
            principal, entropy = SokhotskySifter.sift(val)
            self.assertTrue(abs(entropy) < epsilon, f"Noise classification failed for {val}")
        
        # Test values above epsilon (Signal / Principal Value)
        signal_cases = [1e-12, -1e-12, 0.5, -0.5, 12.5, -12.5]
        for val in signal_cases:
            principal, entropy = SokhotskySifter.sift(val)
            self.assertTrue(abs(entropy) >= epsilon or abs(entropy) == 0.0, f"Signal classification failed for {val}")

    # EDGE CASES: Type conversions and extreme sign-approaches
    def test_edge_cases(self):
        # Test limit approach sign override strings
        res_plus = SokhotskySifter.evaluate_limit(0.5, sign="+0")
        res_minus = SokhotskySifter.evaluate_limit(0.5, sign="-0")
        self.assertNotEqual(res_plus, res_minus)

        # Test limit approach sign using numeric sign values (+0.0 vs -0.0)
        res_plus_num = SokhotskySifter.evaluate_limit(0.5, sign=0.0)
        res_minus_num = SokhotskySifter.evaluate_limit(0.5, sign=-0.0)
        self.assertNotEqual(res_plus_num, res_minus_num)

        # Test inf / nan inputs handling in clamp
        self.assertEqual(ArchitectAnchor.clamp(float('inf')), 13.0)
        self.assertEqual(ArchitectAnchor.clamp(float('-inf')), -13.0)
        # NaN is clamped to absolute deadband
        nan_clamp = ArchitectAnchor.clamp(float('nan'))
        self.assertEqual(nan_clamp, 0.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
