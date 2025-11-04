# Specification: LLM RAG System

## ADDED Requirements

### Requirement: Ollama Integration
The system SHALL integrate with local Ollama server for LLM inference.

#### Scenario: Ollama connection
- **WHEN** system initializes
- **THEN** connection to Ollama server (default: http://localhost:11434) is established
- **AND** connection is verified by health check API
- **AND** error is raised if Ollama is not running

#### Scenario: Model availability check
- **WHEN** system starts
- **THEN** configured model (e.g., qwen2.5:7b) availability is verified
- **AND** error message suggests model pull command if not available
- **AND** fallback to alternative model if configured

#### Scenario: LLM generation
- **WHEN** prompt is sent to Ollama
- **THEN** response is generated using configured model
- **AND** generation parameters (temperature, max_tokens) are applied from config
- **AND** timeout is enforced (default: 30 seconds)

### Requirement: Query Analysis
The system SHALL analyze user queries to extract search intent.

#### Scenario: Simple query parsing
- **WHEN** user asks "生活介護事業所を教えて"
- **THEN** LLM identifies service_type: "生活介護"
- **AND** no other filters are identified
- **AND** structured output is returned (JSON format)

#### Scenario: Complex query parsing
- **WHEN** user asks "小倉北区で送迎ありの就労継続支援B型は？"
- **THEN** LLM identifies:
  - service_type: "就労継続支援B型"
  - district: "小倉北区"
  - transportation: true
- **AND** structured output includes all identified filters

#### Scenario: Ambiguous query handling
- **WHEN** user query is ambiguous (e.g., "良い事業所は？")
- **THEN** LLM requests clarification
- **AND** suggests specific questions user should answer
- **AND** no Neo4j query is executed until clarification

### Requirement: Neo4j Query Generation
The system SHALL generate Neo4j Cypher queries from parsed search intent.

#### Scenario: Simple Cypher generation
- **WHEN** search intent specifies service_type only
- **THEN** Cypher query is generated:
  ```cypher
  MATCH (f:Facility)
  WHERE f.service_type = '生活介護'
  RETURN f
  ORDER BY f.name
  LIMIT 20
  ```

#### Scenario: Complex Cypher generation
- **WHEN** search intent has multiple conditions
- **THEN** Cypher query combines conditions with AND:
  ```cypher
  MATCH (f:Facility)
  WHERE f.service_type = '就労継続支援B型'
    AND f.district = '小倉北区'
    AND f.transportation = true
  RETURN f
  ORDER BY f.name
  LIMIT 20
  ```

#### Scenario: Full-text search Cypher
- **WHEN** search intent includes name/keyword
- **THEN** Cypher uses CONTAINS or regex matching:
  ```cypher
  MATCH (f:Facility)
  WHERE f.name CONTAINS 'keyword' OR f.address CONTAINS 'keyword'
  RETURN f
  LIMIT 20
  ```

### Requirement: Context Construction
The system SHALL construct context for LLM answer generation from Neo4j results.

#### Scenario: Result formatting
- **WHEN** Neo4j query returns facility nodes
- **THEN** each facility is formatted as text block:
  ```
  【事業所名】○○○
  【法人名】△△△
  【サービス種別】就労継続支援B型
  【所在地】小倉北区...
  【電話番号】093-XXX-XXXX
  【定員】20名
  【空き状況】空きあり
  ```

#### Scenario: Context size management
- **WHEN** search results exceed token limit
- **THEN** results are truncated to top N (e.g., 10) most relevant
- **AND** user is informed of total result count
- **AND** pagination information is provided

#### Scenario: Empty results handling
- **WHEN** Neo4j query returns no results
- **THEN** context indicates "該当する事業所が見つかりませんでした"
- **AND** LLM suggests alternative search criteria

### Requirement: Answer Generation
The system SHALL generate natural language answers using LLM with retrieved context.

#### Scenario: Standard answer format
- **WHEN** generating answer from context
- **THEN** answer is structured:
  1. Summary (該当件数、概要)
  2. Individual facility details (リスト形式)
  3. Additional information (送迎、空き状況等)
- **AND** answer is in polite Japanese (敬語)
- **AND** answer length is reasonable (<500 tokens)

#### Scenario: Comparison answer
- **WHEN** user asks for comparison (e.g., "どこが一番良い？")
- **THEN** LLM compares facilities on relevant criteria
- **AND** comparison is objective and data-based
- **AND** LLM does not fabricate information not in context

#### Scenario: Follow-up question handling
- **WHEN** user asks follow-up question
- **THEN** conversation history is included in context
- **AND** LLM maintains context from previous exchanges
- **AND** previous search results are referenced if relevant

### Requirement: Prompt Engineering
The system SHALL use optimized prompts for accurate responses.

#### Scenario: System prompt definition
- **WHEN** system initializes
- **THEN** system prompt includes:
  - Role: "あなたは北九州市の障害福祉サービス事業所の情報提供アシスタントです"
  - Constraints: "データベースにある情報のみを使用し、推測や創作はしないでください"
  - Output format: "わかりやすく、正確に、敬語で回答してください"

#### Scenario: Query analysis prompt
- **WHEN** analyzing user query
- **THEN** prompt requests structured JSON output
- **AND** prompt provides examples of expected output format
- **AND** prompt instructs to handle ambiguity explicitly

#### Scenario: Answer generation prompt
- **WHEN** generating answer
- **THEN** prompt includes:
  - User query
  - Retrieved context (facility data)
  - Instruction to summarize and list facilities
  - Instruction to be factual and avoid hallucination

### Requirement: Error Handling
The system SHALL handle LLM and RAG pipeline errors gracefully.

#### Scenario: Ollama timeout
- **WHEN** LLM generation exceeds timeout
- **THEN** generation is cancelled
- **AND** user receives timeout error message
- **AND** partial response is discarded

#### Scenario: Invalid JSON parsing
- **WHEN** LLM returns invalid JSON for query analysis
- **THEN** error is logged
- **AND** retry is attempted with clarified prompt
- **AND** fallback to keyword-based search if retry fails

#### Scenario: Hallucination detection
- **WHEN** LLM response includes information not in context
- **THEN** warning is logged (if detectable)
- **AND** response is returned with disclaimer if uncertain
- **AND** future prompt engineering addresses hallucination pattern

### Requirement: Performance Optimization
The system SHALL optimize RAG pipeline for acceptable response times.

#### Scenario: Response time target
- **WHEN** user submits query
- **THEN** total response time (query → answer) is <5 seconds
- **AND** breakdown timing is logged: query analysis time, Neo4j time, LLM generation time

#### Scenario: Caching
- **WHEN** identical or similar query is submitted
- **THEN** cached query analysis is reused
- **AND** Neo4j results are cached for 5 minutes
- **AND** cache hit/miss is logged

#### Scenario: Async processing
- **WHEN** processing user query
- **THEN** Neo4j query and LLM operations are async where possible
- **AND** UI shows real-time status (analyzing, searching, generating)
- **AND** user can cancel long-running operations
