// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

/**
 * @title SovereignVault (VaaS Edition)
 * @dev The Layer 1/2 EVM receptor with an integrated Payment Gateway for Verification-as-a-Service.
 * Exclusively owned and operated by Christopher E. Adams / Armada XVII.
 */
contract SovereignVault {
    address public admin;
    address public feeTreasury;
    uint256 public anchorFee;

    struct StateCommitment {
        bytes32 payloadChecksum;
        bytes32 consensusClass;
        uint256 timestamp;
        address anchoredBy;
    }

    mapping(bytes32 => StateCommitment) public commitments;

    uint8 private unlocked = 1;

    // Custom Errors for Gas Optimization
    error Unauthorized();
    error AlreadyAnchored();
    error IncorrectFee(); // Patched: Replaces InsufficientFee for strict pricing
    error TransferFailed();
    error InvalidAddress();
    error Reentrancy();

    event StateAnchored(bytes32 indexed regimeId, bytes32 payloadChecksum, bytes32 consensusClass, address indexed payer, uint256 feePaid, uint256 timestamp);
    event FeeUpdated(uint256 oldFee, uint256 newFee);
    event TreasuryUpdated(address indexed oldTreasury, address indexed newTreasury);

    modifier onlyAdmin() {
        if (msg.sender != admin) revert Unauthorized();
        _;
    }

    modifier nonReentrant() {
        if (unlocked != 1) revert Reentrancy();
        unlocked = 0;
        _;
        unlocked = 1;
    }

    /**
     * @param _initialFee The cost in wei to anchor a state.
     * @param _treasury The cold wallet that receives all VaaS revenue.
     */
    constructor(uint256 _initialFee, address _treasury) {
        if (_treasury == address(0)) revert InvalidAddress();
        admin = msg.sender;
        anchorFee = _initialFee;
        feeTreasury = _treasury;
    }

    /**
     * @dev Administrative controls for adjusting the VaaS toll.
     */
    function setAnchorFee(uint256 _newFee) external onlyAdmin {
        uint256 oldFee = anchorFee;
        anchorFee = _newFee;
        emit FeeUpdated(oldFee, _newFee);
    }

    function setTreasury(address _newTreasury) external onlyAdmin {
        if (_newTreasury == address(0)) revert InvalidAddress();
        address oldTreasury = feeTreasury;
        feeTreasury = _newTreasury;
        emit TreasuryUpdated(oldTreasury, _newTreasury);
    }

    /**
     * @dev The core VaaS Toll Booth. Accepts the fee, routes it to the treasury, and locks the state.
     * In this model, external clients (or the Arbiter on their behalf) can pay to anchor the proof.
     */
    function anchorState(bytes32 regimeId, bytes32 payloadChecksum, bytes32 consensusClass) external payable nonReentrant {
        // 1. CHECKS
        if (msg.value != anchorFee) revert IncorrectFee(); // Reverts on both underpayment and overpayment
        if (commitments[regimeId].timestamp != 0) revert AlreadyAnchored();

        // 2. EFFECTS (Update state before external calls)
        commitments[regimeId] = StateCommitment({
            payloadChecksum: payloadChecksum,
            consensusClass: consensusClass,
            timestamp: block.timestamp,
            anchoredBy: msg.sender
        });

        emit StateAnchored(regimeId, payloadChecksum, consensusClass, msg.sender, msg.value, block.timestamp);

        // 3. INTERACTIONS (Route revenue last)
        (bool success, ) = feeTreasury.call{value: msg.value}("");
        if (!success) revert TransferFailed();
    }
}
