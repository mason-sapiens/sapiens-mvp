# Quick Reference Card - Sapiens MVP

## Setup (30 seconds)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env
python run.py
```

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
DEFAULT_MODEL=gpt-4o              # gpt-4o | gpt-4-turbo | gpt-4o-mini | gpt-5.1
MAX_TOKENS=4096
TEMPERATURE=0.7
```

## API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Create user
curl -X POST "http://localhost:8000/api/users?user_id=USER_ID"

# Send message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "message": "YOUR_MESSAGE"}'

# Get state
curl http://localhost:8000/api/state/USER_ID

# Get project
curl http://localhost:8000/api/project/USER_ID

# Get conversation
curl http://localhost:8000/api/conversation/USER_ID
```

## State Flow

```
onboarding → project_generation → problem_definition →
solution_design → execution → review → completed
```

## Agent Roles

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| ProjectGenerator | Design project | Role, domain | Project proposal |
| ProblemSolutionTutor | Evaluate quality | Problem/Solution | Scores, feedback |
| ExecutionCoach | Track progress | Updates | Next action |
| Reviewer | Evaluate work | Artifacts | Review, resume |
| MainChat | User interface | State, context | Natural language |

## Pass Criteria

- **Problem**: Market relevance ≥6, Clarity ≥6, Feasibility ≥6, Average ≥7
- **Solution**: Coherence ≥6, Innovation ≥6, Feasibility ≥6, Impact ≥6, Average ≥7

## File Locations

```
backend/agents/           # Agent implementations
backend/orchestration/    # State machine & orchestrator
backend/schemas/          # Data models
backend/modules/          # RAG & Logging
backend/api/              # FastAPI endpoints
data/logs/{user_id}/      # User data (generated at runtime)
```

## Common Commands

```bash
# Start server
python run.py

# Run tests
pytest tests/

# Check logs
tail -f data/logs/USER_ID/conversation.jsonl

# View state
cat data/logs/USER_ID/state.json | python -m json.tool
```

## Changing Models

**Edit .env:**
```bash
# GPT-4o (recommended, balanced)
DEFAULT_MODEL=gpt-4o

# GPT-4o Mini (cost optimized)
DEFAULT_MODEL=gpt-4o-mini

# GPT-4 Turbo (highest quality)
DEFAULT_MODEL=gpt-4-turbo

# Future models
DEFAULT_MODEL=gpt-5.1
```

Then restart: `python run.py`

## Cost per Journey

- GPT-4o: ~$0.15-0.45
- GPT-4o Mini: ~$0.01-0.03
- GPT-4 Turbo: ~$0.30-0.90

## Troubleshooting

```bash
# API key not set
export OPENAI_API_KEY=sk-...

# Port in use
lsof -ti:8000 | xargs kill -9

# Dependencies issue
pip install -r requirements.txt --force-reinstall

# Check model
echo $DEFAULT_MODEL
```

## Python API Example

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "test_user"

def chat(msg):
    r = requests.post(f"{BASE_URL}/api/chat",
        json={"user_id": USER_ID, "message": msg})
    return r.json()["response"]

# Usage
print(chat("Product Manager"))
print(chat("FinTech"))
print(chat("skip"))
print(chat("skip"))
```

## JavaScript API Example

```javascript
const chat = async (msg) => {
  const res = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: 'test', message: msg})
  });
  return (await res.json()).response;
};

// Usage
console.log(await chat("Data Scientist"));
```

## Adding a New Agent

1. Create `backend/agents/new_agent.py`
2. Define I/O schemas in `backend/schemas/agent_io.py`
3. Add to orchestrator: `self.new_agent = NewAgent(...)`
4. Call from state handler: `output = self.new_agent.process(input)`

## Adding a New State

1. Add to `StateType` enum in `backend/schemas/state.py`
2. Add transitions in `backend/orchestration/state_machine.py`
3. Add handler in `backend/orchestration/orchestrator.py`
4. Add messaging in `backend/agents/main_chat.py`

## Key Architecture Principles

✓ **State-based orchestration** - Single source of truth
✓ **No agent-to-agent calls** - All through Orchestrator
✓ **Explicit I/O schemas** - Type-safe communication
✓ **Single responsibility** - Each agent has one job
✓ **Comprehensive logging** - Complete audit trail

## Documentation

- **README.md** - Overview
- **QUICKSTART.md** - 5-min setup
- **SYSTEM_OVERVIEW.md** - One-page reference
- **MIGRATION_NOTES.md** - Claude → OpenAI migration
- **docs/ARCHITECTURE.md** - Technical deep dive
- **docs/API.md** - Complete API reference
- **docs/DEPLOYMENT.md** - Production guide
- **docs/MODEL_CONFIGURATION.md** - Model switching guide

## Get Help

- Interactive API docs: http://localhost:8000/docs
- Check logs: `data/logs/{user_id}/`
- View state: `GET /api/state/{user_id}`
- Conversation history: `GET /api/conversation/{user_id}`

## Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong API keys
- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Add rate limiting
- [ ] Use managed database
- [ ] Set billing alerts

---

**Visit http://localhost:8000/docs for interactive API documentation**
