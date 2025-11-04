# Specification: Goal Setting AI

## ADDED Requirements

### Requirement: Goal Data Model
The system SHALL store goal information in Neo4j with SMART evaluation.

#### Scenario: Goal node creation
- **WHEN** goal is created
- **THEN** Goal node is created with unique goal_id
- **AND** node stores goal_type (長期 or 短期)
- **AND** node stores goal_text, goal_reason, evaluation_period, evaluation_method
- **AND** node includes SMART evaluation: is_specific, is_measurable, is_achievable, is_relevant, is_time_bound, smart_score
- **AND** node links to Plan via HAS_GOAL relationship

### Requirement: LLM Goal Generation
The system SHALL generate goal suggestions using LLM based on assessment.

#### Scenario: Long-term goal suggestion
- **WHEN** POST /api/goals/suggest with assessment_id and goal_type="長期"
- **THEN** LLM analyzes assessment results
- **AND** LLM generates 3-5 long-term goal suggestions
- **AND** each suggestion follows SMART principles
- **AND** each suggestion includes rationale and confidence score

#### Scenario: Short-term goal suggestion
- **WHEN** POST /api/goals/suggest with assessment_id and goal_type="短期"
- **THEN** LLM generates short-term goals aligned with long-term goals
- **AND** short-term goals are achievable within 6 months
- **AND** short-term goals contribute to long-term goal achievement

### Requirement: SMART Evaluation
The system SHALL evaluate goals against SMART criteria.

#### Scenario: Automatic SMART analysis
- **WHEN** goal is created or edited
- **THEN** LLM evaluates goal against each SMART criterion
- **AND** boolean flags (is_specific, is_measurable, etc.) are set
- **AND** smart_score (0.0-1.0) is calculated
- **AND** suggestions for improvement are provided if score < 0.8

#### Scenario: SMART improvement suggestions
- **WHEN** goal has low SMART score
- **THEN** LLM generates specific improvement suggestions
- **AND** suggestions address missing or weak SMART criteria
- **AND** revised goal examples are provided

### Requirement: Goal Management API
The system SHALL provide API for goal CRUD operations.

#### Scenario: Create goal
- **WHEN** POST /api/goals with goal data
- **THEN** Goal node is created in Neo4j
- **AND** SMART evaluation is performed
- **AND** goal is linked to plan if plan_id provided

#### Scenario: Evaluate goal
- **WHEN** POST /api/goals/{goal_id}/evaluate
- **THEN** LLM re-evaluates goal with SMART criteria
- **AND** updated SMART scores are returned
- **AND** improvement suggestions are included

### Requirement: Goal UI
The system SHALL provide interface for goal setting.

#### Scenario: Goal suggestion display
- **WHEN** user requests goal suggestions
- **THEN** LLM-generated goals are displayed as cards
- **AND** each card shows: goal_text, rationale, SMART score (visual indicator)
- **AND** user can select, edit, or reject each suggestion
- **AND** selected goals are added to plan

#### Scenario: Goal editor
- **WHEN** user creates or edits goal
- **THEN** form includes: goal_text, goal_reason, evaluation_period, evaluation_method
- **AND** real-time SMART evaluation is displayed as user types
- **AND** SMART score indicator updates dynamically
- **AND** improvement suggestions appear for low-scoring criteria
