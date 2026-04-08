// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title MedicalRecords
 * @dev Store medical record hashes on Polygon blockchain for HealthWatch AI
 */
contract MedicalRecords {
    
    struct Record {
        uint256 id;
        address patient;
        string recordHash;      // Hash of encrypted medical data
        string recordType;      // Type: "vital", "prescription", "diagnosis", etc.
        uint256 timestamp;
        address addedBy;
        bool isActive;
    }
    
    // Mappings
    mapping(uint256 => Record) public records;
    mapping(address => uint256[]) public patientRecords;
    mapping(address => bool) public authorizedProviders;
    
    uint256 public recordCount;
    address public owner;
    
    // Events
    event RecordAdded(
        uint256 indexed id,
        address indexed patient,
        string recordHash,
        string recordType,
        uint256 timestamp,
        address indexed addedBy
    );
    
    event RecordDeactivated(uint256 indexed id, address indexed deactivatedBy);
    event ProviderAuthorized(address indexed provider, address indexed authorizedBy);
    event ProviderRevoked(address indexed provider, address indexed revokedBy);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    modifier onlyAuthorized() {
        require(
            authorizedProviders[msg.sender] || msg.sender == owner,
            "Not authorized"
        );
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedProviders[msg.sender] = true;
    }
    
    /**
     * @dev Add a new medical record to the blockchain
     * @param _patient Patient's Ethereum address
     * @param _recordHash Hash of the encrypted medical record
     * @param _recordType Type of medical record
     * @return Record ID
     */
    function addRecord(
        address _patient,
        string memory _recordHash,
        string memory _recordType
    ) public onlyAuthorized returns (uint256) {
        require(_patient != address(0), "Invalid patient address");
        require(bytes(_recordHash).length > 0, "Record hash cannot be empty");
        
        recordCount++;
        
        records[recordCount] = Record({
            id: recordCount,
            patient: _patient,
            recordHash: _recordHash,
            recordType: _recordType,
            timestamp: block.timestamp,
            addedBy: msg.sender,
            isActive: true
        });
        
        patientRecords[_patient].push(recordCount);
        
        emit RecordAdded(
            recordCount,
            _patient,
            _recordHash,
            _recordType,
            block.timestamp,
            msg.sender
        );
        
        return recordCount;
    }
    
    /**
     * @dev Get a specific medical record
     * @param _id Record ID
     */
    function getRecord(uint256 _id) public view returns (
        uint256 id,
        address patient,
        string memory recordHash,
        string memory recordType,
        uint256 timestamp,
        address addedBy,
        bool isActive
    ) {
        Record memory record = records[_id];
        require(record.id != 0, "Record does not exist");
        
        return (
            record.id,
            record.patient,
            record.recordHash,
            record.recordType,
            record.timestamp,
            record.addedBy,
            record.isActive
        );
    }
    
    /**
     * @dev Get all record IDs for a patient
     * @param _patient Patient's address
     */
    function getPatientRecords(address _patient) 
        public 
        view 
        returns (uint256[] memory) 
    {
        return patientRecords[_patient];
    }
    
    /**
     * @dev Deactivate a record (soft delete)
     * @param _id Record ID
     */
    function deactivateRecord(uint256 _id) public onlyAuthorized {
        require(records[_id].id != 0, "Record does not exist");
        records[_id].isActive = false;
        
        emit RecordDeactivated(_id, msg.sender);
    }
    
    /**
     * @dev Authorize a healthcare provider
     * @param _provider Provider's address
     */
    function authorizeProvider(address _provider) public onlyOwner {
        require(_provider != address(0), "Invalid provider address");
        authorizedProviders[_provider] = true;
        
        emit ProviderAuthorized(_provider, msg.sender);
    }
    
    /**
     * @dev Revoke provider authorization
     * @param _provider Provider's address
     */
    function revokeProvider(address _provider) public onlyOwner {
        authorizedProviders[_provider] = false;
        
        emit ProviderRevoked(_provider, msg.sender);
    }
    
    /**
     * @dev Check if an address is an authorized provider
     * @param _provider Address to check
     */
    function isAuthorizedProvider(address _provider) public view returns (bool) {
        return authorizedProviders[_provider];
    }
    
    /**
     * @dev Get total number of records for a patient
     * @param _patient Patient's address
     */
    function getPatientRecordCount(address _patient) public view returns (uint256) {
        return patientRecords[_patient].length;
    }
}
