// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title GodsEye
 * @notice Immutable Audit Ledger for Multi-Modal AI Provenance & Evidence Authentication
 * @dev Stores cryptographically verified records composed of image hashes, model attestation hashes,
 *      and CV inference results.
 */
contract GodsEye {
    struct IntegrityRecord {
        string imageHash;
        string modelHash;
        string inferenceHash;
        string contributor;
        uint256 timestamp;
    }

    // Mapping from auto-incrementing record ID to IntegrityRecord
    mapping(uint256 => IntegrityRecord) private records;

    // Total records counter
    uint256 public recordCount;

    // Events emitted upon ledger registration
    event RecordRegistered(
        uint256 indexed recordId,
        string imageHash,
        string modelHash,
        string inferenceHash,
        string contributor,
        uint256 timestamp
    );

    /**
     * @notice Registers a verified pipeline output into the immutable ledger
     * @param _imageHash SHA-256 fingerprint of the raw ingested asset
     * @param _modelHash Cryptographic attestation hash of the YOLO weights file
     * @param _inferenceHash Hash of the model's detected bounding box and classification
     * @param _contributor Entity, agency, or department submitting the asset
     * @return The auto-incremented record ID assigned on-chain
     */
    function registerRecord(
        string memory _imageHash,
        string memory _modelHash,
        string memory _inferenceHash,
        string memory _contributor
    ) public returns (uint256) {
        require(bytes(_imageHash).length > 0, "Image hash cannot be empty");
        require(bytes(_modelHash).length > 0, "Model hash cannot be empty");
        require(bytes(_contributor).length > 0, "Contributor identity is mandatory");

        recordCount++;

        records[recordCount] = IntegrityRecord({
            imageHash: _imageHash,
            modelHash: _modelHash,
            inferenceHash: _inferenceHash,
            contributor: _contributor,
            timestamp: block.timestamp
        });

        emit RecordRegistered(
            recordCount,
            _imageHash,
            _modelHash,
            _inferenceHash,
            _contributor,
            block.timestamp
        );

        return recordCount;
    }

    /**
     * @notice Retrieves an on-chain record by ID
     */
    function getRecord(uint256 _recordId)
        public
        view
        returns (
            string memory imageHash,
            string memory modelHash,
            string memory inferenceHash,
            string memory contributor,
            uint256 timestamp
        )
    {
        require(_recordId > 0 && _recordId <= recordCount, "Record does not exist");
        IntegrityRecord memory rec = records[_recordId];
        return (
            rec.imageHash,
            rec.modelHash,
            rec.inferenceHash,
            rec.contributor,
            rec.timestamp
        );
    }

    /**
     * @notice Independent judicial verification method to validate evidence directly on-chain
     */
    function verifyRecord(
        uint256 _recordId,
        string memory _imageHash,
        string memory _modelHash,
        string memory _inferenceHash
    ) public view returns (bool) {
        if (_recordId == 0 || _recordId > recordCount) {
            return false;
        }

        IntegrityRecord memory rec = records[_recordId];

        return (
            keccak256(bytes(rec.imageHash)) == keccak256(bytes(_imageHash)) &&
            keccak256(bytes(rec.modelHash)) == keccak256(bytes(_modelHash)) &&
            keccak256(bytes(rec.inferenceHash)) == keccak256(bytes(_inferenceHash))
        );
    }
}