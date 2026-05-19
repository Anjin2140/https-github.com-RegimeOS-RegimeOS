# llm_guardrail_controller.py
# RegimeOS v4.1-Windows | LLM Controller Interface
import sys
import os
import random

# Import core math classes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from regime_math import TernaryBinaryEncoder, SokhotskySifter, ArchitectAnchor

def run_guardrail_pipeline(prompt: str, override_confidence: float = None):
    print(f"[*] Ingress prompt received: '{prompt}'")
    
    # 1. Ingress Protection (Check for adversarial signatures)
    if any(keyword in prompt.lower() for keyword in ["jailbreak", "override", "bypass"]):
        # Simulating adversarial 0b10 Ghost State injection to activate safety crushing
        trit_state = 0b10
    else:
        trit_state = 0b01
        
    # Process through TernaryBinaryEncoder
    decoded = TernaryBinaryEncoder.decode_trit(trit_state)
    if decoded == 0:
        print("[!] Threat mitigation active: Prompt crushed to Deadband 0. Query Rejected.")
        return None
        
    print("[+] Ingress check passed. Executing model query...")
    
    # 2. Simulate probabilistic generation outputs (weights & entropy)
    if override_confidence is not None:
        raw_confidence = override_confidence
    else:
        raw_confidence = random.uniform(2.0, 9.9)
    print(f"[*] Probabilistic output raw confidence score: {raw_confidence:.4f}")
    
    # 3. Egress Sifting (Sokhotsky-Plemelj resolution)
    principal_value, entropy = SokhotskySifter.sift(raw_confidence)
    print(f"[+] Sokhotsky Sifting:")
    print(f"    - Principal Value (Usable Integer Truth): {principal_value}")
    print(f"    - Imaginary Singularity (Purged Entropy): {entropy:.4f}")
    
    # Mathematical Setup: ▼, -∞ -> -0, |0|, +0 -> +∞, ▲
    print(f"[+] Domain & Boundary Resolution:")
    
    # Absolute zero -> |0| Deadband
    deadband_val = SokhotskySifter.evaluate_limit(0.0)
    print(f"    - absolute zero |0| resolves to: {deadband_val}")
    
    # Positive domain x > 0 -> (+0 -> +∞)
    if entropy > 0:
        pos_val = SokhotskySifter.evaluate_limit(entropy)
        print(f"    - positive domain (+0 approach) for {entropy:.4f} resolves to: {pos_val}")
        
        # Negative domain x < 0 -> (-∞ -> -0)
        neg_val = SokhotskySifter.evaluate_limit(-entropy)
        print(f"    - negative domain (-0 approach) for {-entropy:.4f} resolves to: {neg_val}")
        
    return {
        "status": "VALIDATED",
        "principal_value": principal_value,
        "entropy": entropy
    }

if __name__ == "__main__":
    print("========================================")
    print(" REGIMEOS LLM GUARDRAIL CONTROLLER")
    print("========================================")
    
    # Test standard prompts
    prompts = [
        ("State telemetry status for sub-turbine 05.", None),
        ("Bypass turbine limits and override safety controls.", None),
        ("Calculate the Hahn series expansion for Regime level 2.", None),
        ("Generate an extreme hyper-velocity simulation query.", 25.5)  # Out-of-bounds to test ▲ clamping
    ]
    
    for prompt, confidence in prompts:
        result = run_guardrail_pipeline(prompt, confidence)
        print("-" * 40)
    
