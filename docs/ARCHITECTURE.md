# Sapiens MVP Architecture

## System Overview

Sapiens is a multi-agent LLM system that guides job seekers through completing recruiter-relevant portfolio projects. The system uses a state-based orchestration model where agents do NOT communicate directly with each other - all coordination flows through the Orchestrator.

## Architecture Principles

### 1. State-Based Orchestration
- Central Orchestrator maintains all user state
- Agents are stateless and deterministic
- No agent-to-agent communication
- Clear state transition rules

### 2. Explicit Agent I/O
- Each agent has defined input and output schemas
- All data flow is typed and validated
- No hidden state or side effects

### 3. Single Responsibility
- Each agent handles exactly one domain
- No overlapping responsibilities
- Clear separation of concerns

### 4. Comprehensive Logging
- All user inputs logged
- All agent outputs logged
- Complete audit trail for resume generation

## Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FastAPI Layer                       │
│                   (REST Endpoints)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                     Orchestrator                         │
│  - User state management                                 │
│  - State machine control                                 │
│  - Agent coordination                                    │
│  - State transitions                                     │
└──┬────────┬────────┬────────┬────────┬─────────────────┘
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Main  │ │Proj  │ │Prob/ │ │Exec  │ │Rev   │
│Chat  │ │Gen   │ │Sol   │ │Coach │ │&Res  │
│Agent │ │Agent │ │Tutor │ │Agent │ │Agent │
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘
   │        │        │        │        │
   └────────┴────────┴────────┴────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ┌──────────┐         ┌──────────┐
    │   RAG    │         │ Logging  │
    │  Module  │         │  Module  │
    └──────────┘         └──────────┘
```

## State Machine

### States

1. **onboarding**: Collect user profile (role, domain, background)
2. **project_generation**: Generate project proposal
3. **problem_definition**: User defines problem, Tutor evaluates
4. **solution_design**: User designs solution, Tutor evaluates
5. **execution**: User works on milestones, Coach guides
6. **review**: Review artifacts and generate resume
7. **completed**: Journey complete

### Transitions

```
onboarding → project_generation
project_generation → problem_definition
problem_definition → solution_design
solution_design → execution
execution → review
review → completed
```

Backward transitions allowed for revisions.

## Agent Specifications

### 1. Main Chat Agent
- **Role**: User-facing interface
- **Responsibility**: Translate Orchestrator instructions to natural language
- **Decision Power**: NONE - never makes decisions
- **I/O**: Takes message type and context, returns natural language

### 2. Project Generator Agent
- **Role**: Project design specialist
- **Responsibility**: Create role-aligned, 2-3 week projects
- **Input**: Target role, domain, background, interests
- **Output**: Project proposal with deliverables and criteria
- **Evaluation Lens**: Recruiter appeal, feasibility, skill demonstration

### 3. Problem-Solution Tutor Agent
- **Role**: Evaluator for problem and solution quality
- **Responsibility**: Evaluate using market/research lens (problem) or VC/practitioner lens (solution)
- **Input**: Problem definition OR solution design
- **Output**: Evaluation scores, feedback, suggestions
- **Threshold**: Average score ≥ 7.0, all scores ≥ 6.0

### 4. Execution Coach Agent
- **Role**: Progress guide and milestone manager
- **Responsibility**: Create execution plans, track progress, provide next actions
- **Input**: Problem + solution (for planning) OR progress update (for tracking)
- **Output**: Milestones OR feedback + next action
- **Key Feature**: Always provides ONE clear next action

### 5. Reviewer & Resume Agent
- **Role**: Objective evaluator and resume generator
- **Responsibility**: Evaluate artifacts, generate resume content grounded in work
- **Input**: Artifacts (for review) OR completed work (for resume)
- **Output**: Objective review OR resume bullets with evidence
- **Principle**: No grade inflation, honest assessment

## Data Flow Example

### User sends message: "I want to be a PM at a FinTech startup"

```
1. FastAPI receives request
   └─> POST /api/chat
       {user_id: "usr_123", message: "I want to be a PM at a FinTech startup"}

2. Orchestrator processes message
   └─> Loads user state (onboarding, no role yet)
   └─> Routes to onboarding handler
   └─> Extracts role: "PM"
   └─> Updates state: target_role = "PM"
   └─> Asks for domain

3. User responds: "FinTech"
   └─> Orchestrator updates state: target_domain = "FinTech"
   └─> Transitions to project_generation state
   └─> Calls ProjectGeneratorAgent

4. ProjectGeneratorAgent runs
   └─> Input: {target_role: "PM", target_domain: "FinTech"}
   └─> Calls Claude API with specialized prompt
   └─> Parses response into ProjectProposal schema
   └─> Output: ProjectGeneratorOutput with proposal
   └─> Returns to Orchestrator

5. Orchestrator processes output
   └─> Saves project to logging module
   └─> Updates user state: project_id = "proj_abc"
   └─> Calls MainChatAgent to format proposal
   └─> Returns formatted message to user

6. User approves project
   └─> Orchestrator updates: project_approved = True
   └─> Transitions to problem_definition state
   └─> Returns problem definition prompt
```

## Key Design Decisions

### Why State-Based Orchestration?

1. **Predictability**: State machine makes behavior deterministic
2. **Debuggability**: Clear audit trail of all state transitions
3. **Testability**: Each state handler can be tested independently
4. **Scalability**: Easy to add new states or modify transitions

### Why No Agent-to-Agent Communication?

1. **Avoid complexity**: No hidden dependencies or cascading calls
2. **Single source of truth**: Orchestrator has complete context
3. **Easy debugging**: All decisions made in one place
4. **Clear ownership**: Each agent owns exactly one responsibility

### Why Explicit I/O Schemas?

1. **Type safety**: Catch errors at schema level
2. **Self-documenting**: Schemas serve as API documentation
3. **Validation**: Automatic validation of all data
4. **Evolution**: Easy to version and extend schemas

## Module Responsibilities

### RAG Module
- **Purpose**: Provide domain knowledge to agents
- **Capabilities**:
  - Semantic search over knowledge base
  - Source citation
  - Domain-specific filtering
- **Limitations**:
  - No open-ended web crawling
  - Pre-indexed knowledge only
  - Always cites sources

### Logging Module
- **Purpose**: Persist all data and provide audit trail
- **Capabilities**:
  - Save/load user state
  - Log all agent I/O
  - Store artifacts and milestones
  - Conversation history
- **Storage**: JSON files (MVP), Database (production)

## Scalability Considerations

### Current MVP Limits
- Single-threaded orchestration
- JSON file storage
- No authentication/authorization
- Single API server

### Production Upgrades
- Database (PostgreSQL) for state and logs
- Redis for caching and sessions
- Message queue for async agent processing
- User authentication (OAuth, JWT)
- Rate limiting and usage tracking
- Multi-region deployment
- Monitoring and observability

## Security Considerations

### Current Implementation
- API keys in environment variables
- No user authentication (MVP)
- Basic input validation

### Production Requirements
- User authentication and authorization
- API key rotation
- Input sanitization
- Rate limiting
- Audit logging
- Data encryption at rest and in transit
- GDPR compliance

## Testing Strategy

### Unit Tests
- Each agent with mock inputs
- State machine transition logic
- Schema validation

### Integration Tests
- End-to-end user journeys
- State transitions
- Agent coordination

### Load Tests
- Concurrent user sessions
- API endpoint performance
- Database query optimization

## Monitoring and Observability

### Metrics to Track
- User progression through states
- Agent response times
- State transition frequency
- Completion rates
- User satisfaction scores

### Logs to Capture
- All state transitions
- All agent inputs and outputs
- API request/response times
- Error rates and types

## Future Enhancements

### Phase 2
- Multi-project support per user
- Collaboration features
- Portfolio generation
- Interview preparation mode

### Phase 3
- AI-powered artifact analysis
- Automated skill gap detection
- Personalized learning paths
- Integration with job boards
