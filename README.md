# Sapiens MVP - Project-Based Career Guidance Platform

## Overview

Multi-agent LLM system that guides job seekers through completing a 2-3 week, recruiter-relevant project tailored to their target role.

## Architecture

### State-Based Orchestration
- **No direct agent-to-agent communication**
- All state transitions controlled by Orchestrator
- Deterministic state machine with clear transitions

### Agent System

1. **Orchestrator** - State machine controller
2. **Main Chat Agent** - User-facing conversational interface
3. **Project Generator** - Creates role-aligned project proposals
4. **Problem-Solution Tutor** - Guides problem definition and solution design
5. **Execution Coach** - Tracks milestones and progress
6. **Reviewer & Resume Agent** - Evaluates work and generates resume bullets

### Supporting Modules

- **RAG Module**: Domain knowledge retrieval with source citations
- **Logging Module**: Comprehensive state and artifact tracking

## State Machine

```
onboarding → project_generation → problem_definition → solution_design → execution → review → completed
```

## Tech Stack

- **Backend**: Python 3.10+
- **LLM**: OpenAI GPT-4o (via API)
- **Database**: SQLite (MVP) / PostgreSQL (production)
- **API**: FastAPI
- **Embeddings**: Sentence Transformers
- **Vector Store**: ChromaDB (MVP)

## Project Structure

```
MVP/
├── backend/
│   ├── agents/           # Agent implementations
│   ├── orchestration/    # State machine and orchestrator
│   ├── modules/          # RAG and logging
│   ├── schemas/          # Pydantic models
│   └── api/              # FastAPI endpoints
├── config/               # Configuration files
├── tests/                # Unit and integration tests
├── data/                 # RAG knowledge base
└── docs/                 # Additional documentation
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OPENAI_API_KEY

# Run database migrations
python backend/db/init_db.py

# Start the API server
uvicorn backend.api.main:app --reload
```

## API Endpoints

- `POST /api/users` - Create new user
- `POST /api/chat` - Send message to system
- `GET /api/state/{user_id}` - Get user state
- `GET /api/project/{user_id}` - Get project details
- `GET /api/milestones/{user_id}` - Get execution milestones
- `GET /api/resume/{user_id}` - Get generated resume bullets

## Development Principles

- **Explicit over implicit**: Clear schemas, no magic
- **Separation of concerns**: Each agent has one responsibility
- **Testability**: All agents are stateless and deterministic
- **MVP quality**: Correctness and clarity over premature optimization
