# RegimeOS Bug Bounty Program Rules
### Product of Armada XVII | Owned & Operated by Christopher E. Adams

---

## 🛡️ Program Overview
We are committed to securing the **RegimeOS** Verification-as-a-Service (VaaS) platform. We invite security researchers to audit our smart contracts and portal endpoints to help protect the integrity of our blockchain state anchoring.

## 1. Scope

### In-Scope
Security vulnerabilities found in the following components are eligible for rewards:
- **[SovereignVaultVaaS.sol](file:///C:/RegimeOS/contracts/SovereignVaultVaaS.sol)** (EVM smart contract)
- **FastAPI Web Portal Endpoints**:
  - `/api/health`
  - `/api/notarize`
  - `/api/v1/vaas/submit`
  - `/vaas` (onboarding interface)

### Out-of-Scope
- Vulnerabilities involving local network routing, physical host machine access (ArmadaLite), or standard operating system permissions.
- Denials of service (DoS) or rate-limiting attacks that cause simple resource consumption.
- Client-side styling and CSS bugs.

## 2. Rewards Table

| Severity | Definition | Reward Cap |
| :--- | :--- | :--- |
| **Critical** | Direct fund loss, consensus bypass, or state commitment manipulation | Up to $10,000 / 5 ETH |
| **High** | Unauthorized service disruption or administrative lock manipulation | Up to $2,500 |
| **Medium** | Unauthorized metadata changes or bypassing notary verification | Up to $1,000 |
| **Low** | Minor configuration vulnerabilities or logging discrepancies | Up to $250 |

## 3. Vulnerability Reporting
Please submit all findings directly to Christopher E. Adams or designated STRATSEC security officers. Include:
1. Steps to reproduce the vulnerability (proof-of-concept script).
2. The potential impact of the vulnerability.
3. Recommended remediation steps.
