# Specification: Service Coordination AI

## ADDED Requirements

### Requirement: ServiceNeed Data Model
The system SHALL store service provision details in Neo4j.

#### Scenario: ServiceNeed node creation
- **WHEN** service is added to plan
- **THEN** ServiceNeed node is created with unique service_need_id
- **AND** node stores service_type, service_content, frequency, duration
- **AND** node stores weekly schedule (schedule_monday through schedule_sunday)
- **AND** node links to Facility via PROVIDED_BY relationship
- **AND** node links to Goal via ACHIEVED_THROUGH relationship

### Requirement: LLM Service Suggestion
The system SHALL suggest optimal services using LLM based on goals.

#### Scenario: Service type suggestion
- **WHEN** POST /api/services/suggest with user_id and goal_ids
- **THEN** LLM analyzes user profile and goals
- **AND** LLM suggests appropriate service types
- **AND** each suggestion includes: service_type, frequency, duration, rationale
- **AND** suggestions consider user's disability characteristics and support needs

#### Scenario: Facility recommendation
- **WHEN** service type is determined
- **THEN** system searches Neo4j for matching facilities
- **AND** facilities are filtered by: service_type, district (if specified), capacity
- **AND** top 3-5 recommended facilities are returned
- **AND** recommendations include facility details and selection rationale

### Requirement: Weekly Schedule Generation
The system SHALL generate weekly service schedule automatically.

#### Scenario: Schedule optimization
- **WHEN** multiple services are selected
- **THEN** LLM generates optimal weekly schedule
- **AND** schedule considers: service frequency, user's stamina, transportation time
- **AND** schedule avoids conflicts and overload
- **AND** schedule balances activity and rest days

#### Scenario: Schedule visualization
- **WHEN** schedule is generated
- **THEN** calendar view displays schedule for each day of week
- **AND** each day shows: morning/afternoon/evening activities
- **AND** color coding distinguishes service types
- **AND** user can drag-and-drop to adjust schedule

### Requirement: Service Coordination API
The system SHALL provide API for service planning.

#### Scenario: Service suggestion endpoint
- **WHEN** POST /api/services/suggest
- **THEN** LLM analyzes goals and user profile
- **AND** suggested services and facilities are returned
- **AND** weekly schedule proposal is included
- **AND** response includes confidence scores and alternatives

#### Scenario: Service creation endpoint
- **WHEN** POST /api/services with service details
- **THEN** ServiceNeed node is created
- **AND** relationships to Facility and Goals are established
- **AND** schedule entries are validated for conflicts

### Requirement: Service Coordination UI
The system SHALL provide interface for service planning.

#### Scenario: Service suggestion display
- **WHEN** user requests service suggestions
- **THEN** suggested services are displayed as cards
- **AND** each card shows: service_type, frequency, duration, rationale
- **AND** recommended facilities are listed for each service
- **AND** user can select facilities from dropdown or search

#### Scenario: Weekly schedule editor
- **WHEN** services are selected
- **THEN** weekly calendar view is displayed
- **AND** user can assign services to time slots via drag-and-drop
- **AND** conflicts are highlighted in red
- **AND** schedule summary shows total hours per week
