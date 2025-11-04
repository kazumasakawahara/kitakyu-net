# Specification: Needs Assessment AI

## ADDED Requirements

### Requirement: Assessment Data Model
The system SHALL store assessment information in Neo4j.

#### Scenario: Assessment node creation
- **WHEN** assessment is created for user
- **THEN** Assessment node is created with unique assessment_id
- **AND** node links to User via ASSESSED relationship
- **AND** node stores interview_date and interview_content (raw text)
- **AND** node stores LLM analysis results (analyzed_needs, strengths, challenges)
- **AND** timestamps are automatically set

#### Scenario: ICF model classification
- **WHEN** assessment is analyzed
- **THEN** assessment results are classified using ICF model
- **AND** classification includes: body_functions, activities, participation
- **AND** classification includes: environmental_factors, personal_factors
- **AND** ICF categories are stored as structured data

### Requirement: LLM Needs Analysis
The system SHALL analyze interview content using LLM to identify needs.

#### Scenario: Basic needs identification
- **WHEN** interview content is submitted for analysis
- **THEN** LLM extracts user's expressed needs
- **AND** LLM identifies latent (implicit) needs not explicitly stated
- **AND** needs are categorized (self-realization, social participation, health, etc.)
- **AND** confidence score is provided for each identified need

#### Scenario: Strengths and challenges extraction
- **WHEN** LLM analyzes interview content
- **THEN** user's strengths are identified and listed
- **AND** challenges requiring support are identified
- **AND** each strength/challenge includes supporting evidence from interview
- **AND** strengths and challenges are balanced (not only negative)

#### Scenario: Preferences identification
- **WHEN** interview content includes wishes or preferences
- **THEN** user's preferences are extracted separately
- **AND** family wishes are distinguished from user preferences
- **AND** conflicts between user and family wishes are identified
- **AND** priorities among preferences are assessed

### Requirement: ICF Model Application
The system SHALL classify assessment using ICF (International Classification of Functioning).

#### Scenario: Body functions classification
- **WHEN** assessment mentions physical/mental functions
- **THEN** LLM classifies into ICF body_functions categories
- **AND** specific impairments are documented
- **AND** ICF codes are suggested where applicable

#### Scenario: Activities and participation classification
- **WHEN** assessment mentions daily activities or social participation
- **THEN** LLM classifies into ICF activities and participation categories
- **AND** current activity levels are documented
- **AND** barriers to participation are identified

#### Scenario: Environmental factors analysis
- **WHEN** assessment mentions living situation, family, resources
- **THEN** LLM classifies environmental factors (facilitators and barriers)
- **AND** family support level is assessed
- **AND** community resources accessibility is evaluated

### Requirement: Structured Output Generation
The system SHALL generate structured analysis output from interview content.

#### Scenario: JSON output format
- **WHEN** LLM completes needs analysis
- **THEN** output is returned in structured JSON format
- **AND** JSON includes: analyzed_needs (array), strengths (array), challenges (array)
- **AND** JSON includes: preferences (array), family_wishes (array)
- **AND** JSON includes: icf_classification (object with 5 categories)
- **AND** JSON parsing errors are handled gracefully

#### Scenario: Analysis confidence scoring
- **WHEN** LLM generates analysis
- **THEN** each identified element includes confidence score (0.0-1.0)
- **AND** low-confidence items (< 0.6) are flagged for human review
- **AND** overall analysis quality score is calculated

### Requirement: Analysis Quality Assurance
The system SHALL ensure high-quality needs analysis.

#### Scenario: Completeness check
- **WHEN** analysis is generated
- **THEN** all ICF categories have non-empty content
- **AND** at least 3 needs are identified (or explicit reason given)
- **AND** both strengths and challenges are identified (balanced view)
- **AND** warning is shown if analysis appears incomplete

#### Scenario: Hallucination prevention
- **WHEN** LLM generates analysis
- **THEN** LLM is instructed to base analysis only on interview content
- **AND** LLM must not fabricate information not in interview
- **AND** uncertain inferences are marked as "推測" (speculation)
- **AND** human reviewer is alerted to verify uncertain content

### Requirement: Assessment Prompt Engineering
The system SHALL use optimized prompts for needs analysis.

#### Scenario: System prompt for needs analysis
- **WHEN** needs analysis LLM is invoked
- **THEN** system prompt defines role: "経験豊富な計画相談支援専門員"
- **AND** system prompt instructs ICF model application
- **AND** system prompt requires structured JSON output
- **AND** system prompt prohibits hallucination and speculation

#### Scenario: Few-shot examples
- **WHEN** needs analysis prompt is constructed
- **THEN** prompt includes 2-3 example interview→analysis pairs
- **AND** examples demonstrate good analysis structure
- **AND** examples show ICF classification application
- **AND** examples demonstrate balanced strength/challenge identification

### Requirement: Assessment API Endpoints
The system SHALL provide API for assessment operations.

#### Scenario: Create assessment with analysis
- **WHEN** POST /api/assessments with interview_content and analyze=true
- **THEN** Assessment node is created
- **AND** LLM analysis is performed automatically
- **AND** analysis results are stored in Assessment node
- **AND** complete assessment with analysis is returned

#### Scenario: Re-analyze existing assessment
- **WHEN** POST /api/assessments/{assessment_id}/reanalyze
- **THEN** LLM re-analyzes interview_content with latest prompts
- **AND** previous analysis is preserved (versioned)
- **AND** new analysis results replace current version
- **AND** diff between old and new analysis is shown

#### Scenario: Manual edit of analysis
- **WHEN** PUT /api/assessments/{assessment_id}
- **THEN** human can edit LLM-generated analysis
- **AND** edited fields are marked as "human_edited"
- **AND** original LLM output is preserved for reference
- **AND** edit timestamp and editor are recorded

### Requirement: Assessment UI
The system SHALL provide user interface for assessment creation and analysis.

#### Scenario: Assessment form
- **WHEN** user creates new assessment
- **THEN** form includes: user selection, interview_date, interview_content (textarea)
- **AND** interview_content textarea is large and supports markdown
- **AND** "Analyze with AI" button is prominently displayed
- **AND** form auto-saves draft periodically

#### Scenario: Analysis results display
- **WHEN** LLM analysis completes
- **THEN** results are displayed in organized sections
- **AND** sections include: Needs, Strengths, Challenges, Preferences, ICF Classification
- **AND** each item has confidence indicator (color-coded)
- **AND** low-confidence items are highlighted for review
- **AND** user can edit any analysis result inline

#### Scenario: Analysis loading state
- **WHEN** LLM analysis is in progress
- **THEN** loading indicator is displayed
- **AND** estimated time remaining is shown (if available)
- **AND** user can cancel analysis mid-process
- **AND** partial results are not displayed until complete

### Requirement: Assessment Error Handling
The system SHALL handle assessment analysis errors gracefully.

#### Scenario: LLM timeout
- **WHEN** LLM analysis exceeds timeout (60 seconds)
- **THEN** analysis is cancelled
- **AND** user is notified of timeout
- **AND** option to retry with longer timeout is offered
- **AND** interview content is preserved for retry

#### Scenario: Invalid JSON from LLM
- **WHEN** LLM returns malformed JSON
- **THEN** error is logged with raw LLM output
- **AND** automatic retry is attempted (max 2 retries)
- **AND** if retries fail, user is notified
- **AND** fallback to manual analysis is offered

#### Scenario: Empty or nonsensical analysis
- **WHEN** LLM returns analysis with insufficient content
- **THEN** quality check detects insufficient analysis
- **AND** user is notified that analysis needs improvement
- **AND** prompt refinement is suggested
- **AND** manual analysis override is available
