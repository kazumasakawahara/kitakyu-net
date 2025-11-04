# Specification: Facility Data Processor

## ADDED Requirements

### Requirement: Data Validation
The system SHALL validate facility data for completeness and correctness.

#### Scenario: Required field validation
- **WHEN** processing facility records
- **THEN** required fields (facility_name, corporation_name, facility_number, service_type, address, phone) are verified as non-empty
- **AND** records with missing required fields are flagged with error
- **AND** validation errors are logged with record identifier

#### Scenario: Data type validation
- **WHEN** validating field data types
- **THEN** facility_number is verified as 10-digit string
- **AND** capacity is verified as positive integer or null
- **AND** phone number matches pattern `0\d{1,4}-\d{1,4}-\d{4}` or similar
- **AND** invalid data types are corrected or flagged

#### Scenario: Duplicate detection
- **WHEN** processing multiple records
- **THEN** duplicate facility_number values are detected
- **AND** newer record replaces older record or merge logic is applied
- **AND** duplicate handling is logged

### Requirement: Data Normalization
The system SHALL normalize facility data to consistent format.

#### Scenario: Postal code normalization
- **WHEN** postal code values are processed
- **THEN** format is standardized to `XXX-XXXX` (7 digits with hyphen)
- **AND** invalid postal codes are flagged

#### Scenario: Phone number normalization
- **WHEN** phone number values are processed
- **THEN** format is standardized (e.g., `093-XXX-XXXX` for Kitakyushu)
- **AND** whitespace and special characters are removed
- **AND** hyphens are added in standard positions

#### Scenario: Address normalization
- **WHEN** address values are processed
- **THEN** full address is stored in `address` field
- **AND** district (区) is extracted to `district` field
- **AND** standardized district names (小倉北区, 小倉南区, 八幡東区, 八幡西区, 戸畑区, 門司区, 若松区) are used

#### Scenario: Service type normalization
- **WHEN** service_type values are processed
- **THEN** standardized service type names are used
- **AND** service_category (介護給付, 訓練等給付) is determined
- **AND** mapping from WAM NET terminology to internal terminology is applied

### Requirement: UUID Generation
The system SHALL generate unique identifiers for each facility.

#### Scenario: UUID assignment
- **WHEN** processing facility records
- **THEN** each facility is assigned a UUID v4 identifier
- **AND** UUID is stored in `facility_id` field
- **AND** mapping between facility_number and facility_id is maintained

#### Scenario: Stable UUID for existing facilities
- **WHEN** processing previously imported facilities
- **THEN** existing facility_id is preserved
- **AND** facility_number is used as lookup key

### Requirement: Data Enrichment
The system SHALL enrich facility data with computed fields.

#### Scenario: Timestamp addition
- **WHEN** processing facility records
- **THEN** `created_at` timestamp is added for new records
- **AND** `updated_at` timestamp is added/updated for all records
- **AND** `data_source` field is set to "WAM_NET"

#### Scenario: Availability status initialization
- **WHEN** processing new facility records
- **THEN** `availability_status` is set to "不明" (unknown)
- **AND** status can be manually updated later

### Requirement: Output Generation
The system SHALL generate processed data in Neo4j-compatible format.

#### Scenario: JSON output
- **WHEN** processing completes successfully
- **THEN** processed data is written to `data/processed/facilities_YYYYMMDD.json`
- **AND** JSON structure matches Neo4j import requirements
- **AND** file encoding is UTF-8

#### Scenario: Processing report
- **WHEN** processing completes
- **THEN** summary report is generated with:
  - Total records processed
  - Valid records count
  - Invalid records count
  - Normalization changes count
  - Duplicate detections count
- **AND** report is written to `data/processed/processing_report_YYYYMMDD.txt`
