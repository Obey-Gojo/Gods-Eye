// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title GodsEye
 * @notice Tamper-evident integrity registry for the Gods-Eye project.
 *
 * Stores cryptographic fingerprints of:
 *  - Computer-vision data
 *  - AI models
 *  - Inference results
 *
 * The actual files are NOT stored on the blockchain.
 */
contract GodsEye {

    struct IntegrityRecord {
        string imageHash;
        string modelHash;
        string inferenceHash;
        string contributor;
        uint256 timestamp;
    }

    uint256 public recordCount;

    mapping(uint256 => IntegrityRecord) private records;

    event RecordRegistered(
        uint256 indexed recordId,
        string imageHash,
        string modelHash,
        string inferenceHash,
        string contributor,
        uint256 timestamp
    );

    /**
     * @notice Register a new integrity record.
     */
    function registerRecord(
        string memory _imageHash,
        string memory _modelHash,
        string memory _inferenceHash,
        string memory _contributor
    ) public returns (uint256) {

        require(bytes(_imageHash).length > 0, "Image hash required");
        require(bytes(_modelHash).length > 0, "Model hash required");
        require(
            bytes(_inferenceHash).length > 0,
            "Inference hash required"
        );
        require(
            bytes(_contributor).length > 0,
            "Contributor required"
        );

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
     * @notice Retrieve an integrity record.
     */
    function getRecord(
        uint256 _recordId
    )
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
        require(
            _recordId > 0 && _recordId <= recordCount,
            "Invalid record ID"
        );

        IntegrityRecord memory record = records[_recordId];

        return (
            record.imageHash,
            record.modelHash,
            record.inferenceHash,
            record.contributor,
            record.timestamp
        );
    }

    /**
     * @notice Verify whether current fingerprints match
     *         the fingerprints stored on the blockchain.
     */
    function verifyRecord(
        uint256 _recordId,
        string memory _imageHash,
        string memory _modelHash,
        string memory _inferenceHash
    ) public view returns (bool) {

        require(
            _recordId > 0 && _recordId <= recordCount,
            "Invalid record ID"
        );

        IntegrityRecord memory record = records[_recordId];

        return (
            keccak256(bytes(record.imageHash)) ==
                keccak256(bytes(_imageHash))
            &&
            keccak256(bytes(record.modelHash)) ==
                keccak256(bytes(_modelHash))
            &&
            keccak256(bytes(record.inferenceHash)) ==
                keccak256(bytes(_inferenceHash))
        );
    }
}