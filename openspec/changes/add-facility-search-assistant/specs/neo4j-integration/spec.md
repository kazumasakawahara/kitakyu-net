# Specification: Neo4j Integration

## ADDED Requirements

### Requirement: Database Schema Management
The system SHALL manage Neo4j database schema for facility data.

#### Scenario: Constraint creation
- **WHEN** database is initialized
- **THEN** unique constraint on `Facility.facility_id` is created
- **AND** constraint name is `facility_id_unique`
- **AND** duplicate facility_id insertion is rejected

#### Scenario: Index creation
- **WHEN** database is initialized
- **THEN** indexes are created on frequently queried fields:
  - `Facility.name`
  - `Facility.service_type`
  - `Facility.district`
  - `Facility.facility_number`
- **AND** index names follow convention `facility_{field_name}`

#### Scenario: Schema validation
- **WHEN** schema initialization is executed
- **THEN** existing constraints and indexes are checked
- **AND** missing schema elements are created
- **AND** schema status is logged

### Requirement: Facility Node Import
The system SHALL import facility data as Neo4j nodes.

#### Scenario: Bulk import
- **WHEN** processed facility data is imported
- **THEN** MERGE operation is used to avoid duplicates (based on facility_id)
- **AND** all properties are set from processed data
- **AND** import is performed in batches of 100 nodes for efficiency

#### Scenario: Property mapping
- **WHEN** creating/updating Facility nodes
- **THEN** all properties from processed data are mapped:
  - facility_id, name, corporation_name, facility_number
  - service_type, service_category, postal_code, address, district
  - phone, fax (if available), capacity, availability_status
  - created_at, updated_at, data_source
- **AND** null values are handled appropriately (not stored or stored as null)

#### Scenario: Update existing nodes
- **WHEN** importing data for existing facility_id
- **THEN** existing node properties are updated
- **AND** created_at is preserved
- **AND** updated_at is set to current timestamp
- **AND** update operation is logged

### Requirement: Import Error Handling
The system SHALL handle import errors gracefully.

#### Scenario: Constraint violation
- **WHEN** import operation violates constraint
- **THEN** specific error is logged with facility identifier
- **AND** import continues with remaining records
- **AND** error summary is provided at end

#### Scenario: Connection error
- **WHEN** Neo4j connection fails during import
- **THEN** error is logged with connection details
- **AND** import is retried up to 3 times with exponential backoff
- **AND** user is notified if retry fails

#### Scenario: Transaction rollback
- **WHEN** batch import fails
- **THEN** transaction is rolled back for that batch
- **AND** error details are logged
- **AND** import continues with next batch

### Requirement: Query Functions
The system SHALL provide query functions for facility search.

#### Scenario: Search by service type
- **WHEN** query requests facilities of specific service_type
- **THEN** all matching facilities are returned
- **AND** results include all node properties
- **AND** results are ordered by name (alphabetically)

#### Scenario: Search by district
- **WHEN** query requests facilities in specific district
- **THEN** all facilities with matching district value are returned
- **AND** results include facility name, service_type, address, phone

#### Scenario: Complex search
- **WHEN** query requests facilities with multiple conditions (e.g., service_type AND district AND availability_status)
- **THEN** all conditions are applied with AND logic
- **AND** empty result set is returned if no matches found
- **AND** query performance is optimized using indexes

#### Scenario: Full-text search
- **WHEN** query requests facilities by name or address keyword
- **THEN** CONTAINS or fuzzy matching is used
- **AND** results are ranked by relevance
- **AND** case-insensitive matching is applied

### Requirement: Database Statistics
The system SHALL provide database statistics for monitoring.

#### Scenario: Count facilities
- **WHEN** statistics are requested
- **THEN** total count of Facility nodes is returned
- **AND** count by service_type is returned
- **AND** count by district is returned

#### Scenario: Data freshness check
- **WHEN** data freshness is checked
- **THEN** oldest updated_at timestamp is returned
- **AND** newest updated_at timestamp is returned
- **AND** facilities with data_source "WAM_NET" vs "手動入力" are counted separately

### Requirement: Database Backup
The system SHALL support database backup operations.

#### Scenario: Export to JSON
- **WHEN** backup is requested
- **THEN** all Facility nodes are exported to JSON file
- **AND** file is written to `data/backups/neo4j_backup_YYYYMMDD_HHMMSS.json`
- **AND** backup includes all properties and metadata

#### Scenario: Export validation
- **WHEN** backup export completes
- **THEN** exported record count matches database count
- **AND** validation report is generated
- **AND** user is notified of backup success/failure
