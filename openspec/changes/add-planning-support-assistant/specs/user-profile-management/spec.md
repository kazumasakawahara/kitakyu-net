# Specification: User Profile Management

## ADDED Requirements

### Requirement: User Data Model
The system SHALL store comprehensive user (利用者) information in Neo4j.

#### Scenario: User node creation
- **WHEN** new user is registered
- **THEN** User node is created with unique user_id (UUID)
- **AND** node includes basic information: name, kana, birth_date, gender
- **AND** node includes disability information: disability_type, disability_grade, support_level
- **AND** node includes contact information: phone, address, guardian details
- **AND** timestamps (created_at, updated_at) are automatically set

#### Scenario: User data validation
- **WHEN** user data is submitted
- **THEN** required fields are validated (name, birth_date, disability_type)
- **AND** birth_date format is validated (YYYY-MM-DD)
- **AND** age is calculated automatically from birth_date
- **AND** validation errors return clear error messages

#### Scenario: User data relationships
- **WHEN** user has existing plans
- **THEN** User node connects to Plan nodes via HAS_PLAN relationship
- **AND** relationship preserves plan history
- **AND** current active plan is identifiable

### Requirement: User List and Search
The system SHALL provide user list and search functionality.

#### Scenario: User list retrieval
- **WHEN** user list is requested
- **THEN** all users are returned sorted by name (alphabetical)
- **AND** each user includes: user_id, name, age, disability_type, updated_at
- **AND** pagination is supported (page size: 20)

#### Scenario: User search by name
- **WHEN** search query is submitted
- **THEN** users matching name or kana are returned
- **AND** partial matching is supported (e.g., "山田" matches "山田太郎")
- **AND** case-insensitive search is performed

#### Scenario: User filter by criteria
- **WHEN** filter is applied (disability_type, support_level, age_range)
- **THEN** users matching all filter criteria are returned
- **AND** multiple filters can be combined with AND logic
- **AND** result count is included in response

### Requirement: User Detail View
The system SHALL provide detailed user information retrieval.

#### Scenario: User detail retrieval
- **WHEN** user detail is requested by user_id
- **THEN** complete user information is returned
- **AND** related plans are included (if any)
- **AND** most recent assessment is included (if any)
- **AND** 404 error is returned if user_id not found

#### Scenario: User history view
- **WHEN** user history is requested
- **THEN** all past plans are returned chronologically
- **AND** plan status for each period is included
- **AND** assessment history is included
- **AND** service usage history is included

### Requirement: User CRUD Operations
The system SHALL support Create, Read, Update, Delete operations for users.

#### Scenario: Create new user
- **WHEN** POST /api/users with valid data
- **THEN** new User node is created in Neo4j
- **AND** unique user_id (UUID) is generated
- **AND** created user data is returned with 201 status
- **AND** validation errors return 400 status

#### Scenario: Update existing user
- **WHEN** PUT /api/users/{user_id} with partial data
- **THEN** specified fields are updated
- **AND** updated_at timestamp is refreshed
- **AND** unchanged fields are preserved
- **AND** 404 error if user_id not found

#### Scenario: Delete user
- **WHEN** DELETE /api/users/{user_id}
- **THEN** user deletion is confirmed by user
- **AND** related plans are marked as archived (not deleted)
- **AND** soft delete is performed (user marked as deleted, not removed)
- **AND** 200 status with confirmation message returned

### Requirement: User Data Privacy
The system SHALL protect user personal information.

#### Scenario: Access control
- **WHEN** user data is accessed
- **THEN** access is logged with timestamp and accessor
- **AND** sensitive fields (guardian info, medical details) require explicit permission
- **AND** unauthorized access returns 403 error

#### Scenario: Data anonymization
- **WHEN** user data is exported for analysis
- **THEN** personally identifiable information is anonymized
- **AND** anonymization is reversible only by authorized users
- **AND** anonymized data retains statistical validity

#### Scenario: Audit trail
- **WHEN** user data is created, updated, or deleted
- **THEN** audit log entry is created
- **AND** log includes: action type, user_id, timestamp, changed fields
- **AND** audit logs are immutable and retained for compliance

### Requirement: User Import/Export
The system SHALL support bulk user data operations.

#### Scenario: CSV import
- **WHEN** user CSV file is uploaded
- **THEN** each row is validated before import
- **AND** valid users are imported as new User nodes
- **AND** duplicate users (by name + birth_date) are skipped with warning
- **AND** import summary includes: total, imported, skipped, errors

#### Scenario: User data export
- **WHEN** user data export is requested
- **THEN** all users (or filtered subset) are exported to CSV
- **AND** export includes all non-sensitive fields
- **AND** export filename includes timestamp
- **AND** download link is returned

### Requirement: User Profile UI
The system SHALL provide user-friendly user management interface.

#### Scenario: User list page
- **WHEN** user navigates to user list page
- **THEN** users are displayed in table format
- **AND** table includes: name, age, disability_type, last_updated
- **AND** table supports sorting by each column
- **AND** search and filter controls are provided
- **AND** "Add New User" button is visible

#### Scenario: User detail page
- **WHEN** user clicks on user in list
- **THEN** detail page displays complete user information
- **AND** information is organized in sections: Basic Info, Disability Info, Contact Info
- **AND** "Edit" and "Create Plan" buttons are visible
- **AND** related plans are listed below user information

#### Scenario: User form
- **WHEN** user creates or edits user profile
- **THEN** form includes all required and optional fields
- **AND** form uses appropriate input types (date picker, dropdown, etc.)
- **AND** form provides inline validation feedback
- **AND** form submission shows loading state
- **AND** success/error message is displayed after submission
