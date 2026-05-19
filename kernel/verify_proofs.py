# verify_proofs.py
# RegimeOS v4.1-Windows | Math Invariants Verification Suite
import sys
import unittest

# Import core math classes
from regime_math import TernaryBinaryEncoder, SokhotskySifter, ArchitectAnchor

class TestRegimeMathProofs(unittest.TestCase):

    # PROOF 1: BOUNDEDNESS INVARIANT (Layer 1)
    def test_layer1_invariant(self):
        # Test extreme inputs clamp to bounds [-13, 13]
        for val in [-100.0, -50.5, -13.0, -5.0, 0.0, 5.0, 13.0, 50.5, 100.0]:
            clamped = ArchitectAnchor.clamp(val)
            self.assertTrue(-13.0 <= clamped <= 13.0, f"Clamp failed for value: {val}")

    # PROOF 2: DISCRETE LIPSCHITZ STEP BOUND (Layer 2)
    def test_layer2_step_bound(self):
        # Verify that single-step transition from clamped state changes state by at most 1 unit
        for state in range(-13, 14):
            for delta in [-1, 0, 1]:
                next_state = ArchitectAnchor.clamp(state + delta)
                self.assertTrue(abs(next_state - state) <= 1, f"Step limit failed for state={state}, delta={delta}")

    # PROOF 3: NUMERICAL STABILITY (Layer 3)
    def test_layer3_no_div_zero(self):
        # Sokhotsky-Plemelj division should never raise ZeroDivisionError and should return valid limits
        for x in [0.0, 1e-20, -1e-20, 5.0, -5.0]:
            try:
                result = SokhotskySifter.evaluate_limit(x)
                if x == 0.0:
                    self.assertEqual(result, 0)
                else:
                    self.assertIsNotNone(result)
            except ZeroDivisionError:
                self.fail(f"ZeroDivisionError raised for x={x}")

    # PROOF 4: LOGICAL HIERARCHY / THRESHOLD FILTER (Layer 4)
    def test_layer4_threshold_logic(self):
        # Verification that sifting correctly separates principal value from imaginary noise at threshold 1e-13
        epsilon = 1e-13
        # Value strictly below epsilon (Noise / Imaginary Singularity)
        noise_val = 5e-14
        principal, entropy = SokhotskySifter.sift(noise_val)
        self.assertTrue(abs(entropy) < epsilon)
        
        # Value above epsilon (Signal / Principal Value)
        signal_val = 0.5
        principal, entropy = SokhotskySifter.sift(signal_val)
        self.assertTrue(abs(entropy) >= epsilon)

if __name__ == '__main__':
    unittest.main(verbosity=2)
