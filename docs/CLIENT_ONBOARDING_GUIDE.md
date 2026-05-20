# VaaS Developer Integration & Client Onboarding Guide
### Product of Armada XVII | Owned & Operated by Christopher E. Adams

---

## 🚀 Welcome to Verification-as-a-Service (VaaS)
The VaaS portal allows decentralized clients to submit cryptographic proofs of state consistency directly to the **RegimeOS** engine. The engine processes these proofs and automatically anchors the state invariants on-chain to the EVM network.

## 1. Onboarding Protocol
To begin submitting transactions to the VaaS gateway:
1. **Request API Credentials**: Coordinate with Christopher E. Adams to receive your authorized `regimeId` and access token.
2. **Establish Fee Treasury Address**: VaaS fee settlements are automatically routed to our audited 2-of-3 Gnosis Safe multi-signature wallet. Ensure your client contract or integration script is funded with Sepolia ETH (testnet) or Base ETH (mainnet) to cover the anchoring toll.
3. **Verify Host Network Binding**: Ensure your systems can route to the wildcard endpoint at `http://10.0.0.170:5001` (HTTP fallback) or securely over `https://10.0.0.170:5000` (HTTPS).

## 2. API Integration Reference

### State Anchoring Endpoint
Submit state commitments to the VaaS gateway.

* **Endpoint**: `POST /api/v1/vaas/submit`
* **Content-Type**: `application/json`

#### Request Payload
```json
{
  "task_id": "client-task-1001",
  "payload_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "consensus_class": "ARMADA_XVII_STABILITY_LOCK"
}
```
* `task_id` (string, required): A unique ID for the verification task.
* `payload_checksum` (string, required): The 64-character lowercase hexadecimal hash of your dataset.
* `consensus_class` (string, required): Domain routing classification tag.

#### Response Output (`200 OK`)
```json
{
  "status": "completed",
  "tx_hash": "0x4ad0edd333bc4d18038ec7a6bdf98c047b3c08c677027cd64467ce7396b1b53e"
}
```

## 3. Web UI Integration
The onboarding page is served directly at:
* **https://localhost:5000/vaas** (Secure client landing portal)
* The portal features a dark-mode glassmorphism interface enabling manual proof submissions and live anchoring status verification.
