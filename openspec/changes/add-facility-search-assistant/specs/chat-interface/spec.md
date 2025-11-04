# Specification: Chat Interface

## ADDED Requirements

### Requirement: Streamlit Chat UI
The system SHALL provide a web-based chat interface using Streamlit.

#### Scenario: Chat window layout
- **WHEN** user accesses the application
- **THEN** page displays:
  - Application title and description at top
  - Chat message area in center (scrollable)
  - User input field at bottom
  - Sidebar with options/filters (collapsible)
- **AND** layout is responsive on different screen sizes

#### Scenario: Message display
- **WHEN** messages are displayed
- **THEN** user messages are shown on right with user avatar
- **AND** assistant messages are shown on left with assistant avatar
- **AND** messages support markdown formatting (bold, lists, links)
- **AND** timestamps are shown for each message

#### Scenario: Input handling
- **WHEN** user types message and presses Enter or clicks Send
- **THEN** message is added to conversation history
- **AND** message is sent to backend API
- **AND** input field is cleared
- **AND** send button is disabled during processing

### Requirement: Conversation History Management
The system SHALL maintain conversation history within session.

#### Scenario: Session state persistence
- **WHEN** user sends multiple messages
- **THEN** all messages are stored in session state
- **AND** conversation history is preserved during session
- **AND** page refresh clears history (or persists with local storage)

#### Scenario: History display
- **WHEN** conversation history exists
- **THEN** all previous messages are displayed in chronological order
- **AND** scroll position automatically moves to latest message
- **AND** user can scroll up to view history

#### Scenario: Clear history
- **WHEN** user clicks "Clear Conversation" button
- **THEN** all messages are removed from display and session state
- **AND** confirmation dialog is shown before clearing
- **AND** user can start new conversation

### Requirement: Search Results Display
The system SHALL display facility search results in user-friendly format.

#### Scenario: List format display
- **WHEN** assistant responds with facility list
- **THEN** results are displayed as formatted list with:
  - Facility name (bold)
  - Service type, district
  - Phone number
  - Availability status (highlighted if "空きあり")
- **AND** each facility is clearly separated

#### Scenario: Table format display
- **WHEN** user requests tabular view or results are numerous
- **THEN** results are displayed in sortable table with columns:
  - Name, Service Type, District, Phone, Availability
- **AND** table supports sorting by clicking column headers
- **AND** table is scrollable if too many rows

#### Scenario: Detail view
- **WHEN** user clicks on facility name
- **THEN** detailed information modal/expander opens showing:
  - All facility properties
  - Map link (if address available)
  - Contact information
- **AND** user can close detail view to return to list

#### Scenario: Empty results
- **WHEN** search returns no results
- **THEN** message clearly states "該当する事業所が見つかりませんでした"
- **AND** suggestions for alternative search criteria are provided
- **AND** no error state is shown (expected behavior)

### Requirement: Loading and Status Indicators
The system SHALL provide clear feedback during processing.

#### Scenario: Loading indicator
- **WHEN** query is being processed
- **THEN** loading spinner or progress indicator is shown
- **AND** status text indicates current operation (例: "検索中...", "回答生成中...")
- **AND** send button is disabled during processing

#### Scenario: Processing time display
- **WHEN** response is received
- **THEN** processing time is displayed (e.g., "回答生成: 3.2秒")
- **AND** time is shown in assistant message footer

#### Scenario: Error display
- **WHEN** error occurs (network, timeout, etc.)
- **THEN** error message is displayed in chat as assistant message
- **AND** error is user-friendly (not technical stack trace)
- **AND** suggestion for retry or alternative action is provided

### Requirement: Sample Questions
The system SHALL provide sample questions to guide users.

#### Scenario: Quick question buttons
- **WHEN** conversation is empty or minimal
- **THEN** sample question buttons are displayed above input field:
  - "生活介護事業所を教えて"
  - "小倉北区の就労支援は？"
  - "送迎ありの事業所を探しています"
- **AND** clicking button populates input field and sends query

#### Scenario: Help text
- **WHEN** user clicks help icon or "使い方" button
- **THEN** help modal displays:
  - How to use the chat interface
  - Example questions and query patterns
  - Tips for better search results
- **AND** help can be dismissed easily

### Requirement: Sidebar Options
The system SHALL provide sidebar with configuration options.

#### Scenario: Filter options
- **WHEN** sidebar is opened
- **THEN** user can select filters:
  - District (multi-select)
  - Service type (multi-select)
  - Availability status (checkbox: "空きあり" only)
  - Transportation (checkbox: "送迎あり" only)
- **AND** filters are applied to subsequent searches
- **AND** active filters are displayed in main area

#### Scenario: Display settings
- **WHEN** user accesses display settings in sidebar
- **THEN** user can toggle:
  - Result format (list vs table)
  - Show/hide timestamps
  - Compact vs expanded view
- **AND** settings are persisted in session

#### Scenario: System information
- **WHEN** sidebar shows system information section
- **THEN** displayed information includes:
  - Connected database status
  - Total facility count
  - Data last updated date
  - Ollama model in use

### Requirement: Backend API Integration
The system SHALL communicate with FastAPI backend.

#### Scenario: Chat endpoint call
- **WHEN** user sends message
- **THEN** POST request to `/api/chat` with:
  - message: user query
  - history: conversation history (optional)
  - filters: active filters (optional)
- **AND** response is parsed and displayed
- **AND** error handling for network failures

#### Scenario: Facility search endpoint call
- **WHEN** direct facility search is requested (optional feature)
- **THEN** GET request to `/api/facilities/search` with query parameters
- **AND** results are displayed in table format
- **AND** results can be clicked for details

#### Scenario: API error handling
- **WHEN** API returns error status (4xx, 5xx)
- **THEN** error message is extracted from response
- **AND** user-friendly error is displayed in chat
- **AND** retry option is provided if appropriate

### Requirement: Accessibility
The system SHALL be accessible to users with diverse needs.

#### Scenario: Keyboard navigation
- **WHEN** user navigates using keyboard only
- **THEN** all interactive elements are reachable via Tab
- **AND** Enter key sends message from input field
- **AND** Escape key closes modals/dialogs

#### Scenario: Screen reader support
- **WHEN** screen reader is active
- **THEN** all UI elements have appropriate ARIA labels
- **AND** message roles are announced (user/assistant)
- **AND** loading states are announced

#### Scenario: Contrast and readability
- **WHEN** application is displayed
- **THEN** text has sufficient contrast ratio (WCAG AA)
- **AND** font size is readable (minimum 14px)
- **AND** interactive elements have clear focus indicators

### Requirement: Performance
The system SHALL provide responsive user experience.

#### Scenario: Page load time
- **WHEN** application is accessed
- **THEN** initial page load completes in <2 seconds
- **AND** chat interface is interactive immediately
- **AND** backend connection is established in background

#### Scenario: Message rendering
- **WHEN** new message is added
- **THEN** message appears immediately (<100ms)
- **AND** markdown rendering is fast
- **AND** long messages don't freeze UI

#### Scenario: Scrolling performance
- **WHEN** conversation has many messages (>50)
- **THEN** scrolling remains smooth
- **AND** virtualization is used if necessary for performance
- **AND** old messages are lazy-loaded if needed
