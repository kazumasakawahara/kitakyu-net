# Specification: Document Generation

## ADDED Requirements

### Requirement: Document Template Management
The system SHALL manage Word templates for plan documents.

#### Scenario: Template storage
- **WHEN** system initializes
- **THEN** templates are loaded from backend/documents/templates/
- **AND** templates include: plan_form1.docx (様式1), plan_form5.docx (様式5)
- **AND** templates contain placeholders for dynamic content
- **AND** templates follow official disability welfare service formats

#### Scenario: Template validation
- **WHEN** template is loaded
- **THEN** required placeholders are verified to exist
- **AND** template structure is validated
- **AND** error is raised if template is invalid or missing

### Requirement: Plan Form 1 Generation
The system SHALL generate "サービス等利用計画書" (Plan Form 1).

#### Scenario: Form 1 data population
- **WHEN** POST /api/documents/plan-form1 with plan_id
- **THEN** plan data is retrieved from Neo4j (user, assessment, goals, services)
- **AND** template placeholders are replaced with actual data
- **AND** long-term and short-term goals are formatted correctly
- **AND** service details are listed with providers

#### Scenario: Form 1 DOCX generation
- **WHEN** format=docx is specified
- **THEN** Word document is generated using python-docx
- **AND** formatting matches template styles
- **AND** document is saved to temporary location
- **AND** download URL is returned

#### Scenario: Form 1 PDF generation
- **WHEN** format=pdf is specified
- **THEN** Word document is generated first
- **AND** Word is converted to PDF using reportlab
- **AND** PDF maintains formatting and layout
- **AND** download URL is returned

### Requirement: Plan Form 5 Generation
The system SHALL generate "週間計画表" (Weekly Plan Form 5).

#### Scenario: Form 5 schedule population
- **WHEN** POST /api/documents/plan-form5 with plan_id
- **THEN** weekly schedule is retrieved from ServiceNeed nodes
- **AND** schedule is formatted as table (days × time periods)
- **AND** each cell shows: service type, provider, duration
- **AND** empty cells are handled appropriately

#### Scenario: Form 5 document generation
- **WHEN** weekly plan document is generated
- **THEN** template is populated with schedule data
- **AND** document is generated in requested format (docx or pdf)
- **AND** download URL is returned

### Requirement: Document Export API
The system SHALL provide API endpoints for document generation.

#### Scenario: Generate Plan Form 1
- **WHEN** POST /api/documents/plan-form1 with {plan_id, format}
- **THEN** Plan Form 1 is generated in specified format
- **AND** file is saved to temporary downloads directory
- **AND** response includes: file_url, filename, file_size, expiry_time
- **AND** file expires after 1 hour

#### Scenario: Generate Plan Form 5
- **WHEN** POST /api/documents/plan-form5 with {plan_id, format}
- **THEN** Plan Form 5 is generated in specified format
- **AND** file is saved to temporary downloads directory
- **AND** response includes download details

#### Scenario: Generate complete plan package
- **WHEN** POST /api/documents/plan-package with plan_id
- **THEN** both Form 1 and Form 5 are generated
- **AND** files are packaged into ZIP archive
- **AND** ZIP download URL is returned

### Requirement: Document Generation Error Handling
The system SHALL handle document generation failures gracefully.

#### Scenario: Missing plan data
- **WHEN** plan has incomplete data (missing goals or services)
- **THEN** generation is cancelled with clear error message
- **AND** user is informed which data is missing
- **AND** link to edit plan is provided

#### Scenario: Template rendering error
- **WHEN** template rendering fails
- **THEN** error is logged with details
- **AND** user receives generic error message
- **AND** fallback to manual document creation is suggested

#### Scenario: File system error
- **WHEN** document cannot be saved due to file system issue
- **THEN** error is logged
- **AND** retry is attempted (max 2 retries)
- **AND** user is notified if retry fails

### Requirement: Document UI
The system SHALL provide interface for document generation and download.

#### Scenario: Document preview
- **WHEN** user navigates to plan document page
- **THEN** preview of generated document is displayed
- **AND** preview shows actual content without placeholders
- **AND** user can switch between Form 1 and Form 5 preview

#### Scenario: Document export controls
- **WHEN** user is on document page
- **THEN** export buttons are displayed: "Word出力", "PDF出力"
- **AND** clicking button triggers document generation
- **AND** loading indicator is shown during generation
- **AND** download link appears when generation completes

#### Scenario: Document download
- **WHEN** download link is clicked
- **THEN** browser initiates file download
- **AND** filename includes: plan_number, form_type, date (e.g., plan_001_form1_20251031.docx)
- **AND** download completes successfully

### Requirement: Document Generation Performance
The system SHALL optimize document generation for acceptable performance.

#### Scenario: Generation time target
- **WHEN** document generation is requested
- **THEN** generation completes within 10 seconds for Form 1
- **AND** generation completes within 5 seconds for Form 5
- **AND** progress indicator updates during generation

#### Scenario: Concurrent generation
- **WHEN** multiple users request document generation simultaneously
- **THEN** requests are queued and processed
- **AND** system does not become unresponsive
- **AND** each user receives their document without errors
