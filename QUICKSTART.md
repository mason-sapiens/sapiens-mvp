# Sapiens MVP - Quick Start Guide

## What is Sapiens?

Sapiens is a multi-agent AI system that guides job seekers through completing a 2-3 week, recruiter-relevant portfolio project. It uses a sophisticated state-machine architecture with specialized AI agents to provide personalized guidance from idea to resume-ready deliverable.

## 5-Minute Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get one at: https://platform.openai.com/api-keys
echo "OPENAI_API_KEY=sk-..." >> .env
```

### 3. Start the Server

```bash
python run.py
```

The API will start at `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation.

## Your First Project

### Option 1: Using cURL

```bash
# 1. Create a user
curl -X POST "http://localhost:8000/api/users?user_id=demo_001"

# 2. Start conversation - provide target role
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_001",
    "message": "Product Manager"
  }'

# 3. Provide target domain
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_001",
    "message": "FinTech"
  }'

# 4. Skip background (or provide your background)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_001",
    "message": "skip"
  }'

# 5. Skip interests (or provide your interests)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_001",
    "message": "skip"
  }'

# System will now generate a project proposal!

# 6. Check your project
curl "http://localhost:8000/api/project/demo_001"
```

### Option 2: Using Python

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "demo_002"

def chat(message):
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"user_id": USER_ID, "message": message}
    )
    return response.json()["response"]

# Create user
requests.post(f"{BASE_URL}/api/users?user_id={USER_ID}")

# Onboarding
print(chat("Data Scientist"))
print(chat("Healthcare"))
print(chat("skip"))
print(chat("skip"))

# System generates project - approve it
print(chat("yes"))

# Continue the journey!
```

### Option 3: Using JavaScript/TypeScript

```javascript
const BASE_URL = "http://localhost:8000";
const USER_ID = "demo_003";

async function chat(message) {
  const response = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: USER_ID, message }),
  });
  const data = await response.json();
  console.log(data.response);
  return data.response;
}

// Onboarding
await chat("Marketing Manager");
await chat("E-commerce");
await chat("skip");
await chat("skip");

// Approve project
await chat("yes");
```

## Understanding the Journey

Your user goes through these states:

1. **Onboarding** → Collect profile (role, domain, background)
2. **Project Generation** → AI generates tailored project proposal
3. **Problem Definition** → User defines problem, AI evaluates quality
4. **Solution Design** → User designs solution, AI evaluates approach
5. **Execution** → User works on milestones with AI coaching
6. **Review** → AI reviews artifacts and generates resume bullets
7. **Completed** → User receives resume-ready content!

## Key Features

### 🎯 Personalized Projects
- Tailored to target role and domain
- Completable in 2-3 weeks
- Recruiter-relevant deliverables

### 🧠 Multi-Agent AI System
- **Project Generator**: Designs role-aligned projects
- **Problem-Solution Tutor**: Evaluates quality with specific lenses
- **Execution Coach**: Tracks progress, provides clear next actions
- **Reviewer**: Objectively evaluates and generates resume content
- **Main Chat**: Natural language interface

### 🔄 State Machine Architecture
- Deterministic state transitions
- Complete audit trail
- Easy to debug and extend

### 📝 Resume Generation
- Grounded in actual work done
- No exaggeration or unsupported claims
- 3-5 strong bullets with evidence

## API Endpoints

```
GET  /health                        # Health check
POST /api/users                     # Create user
POST /api/chat                      # Send message
GET  /api/state/{user_id}           # Get user state
GET  /api/project/{user_id}         # Get project details
GET  /api/conversation/{user_id}    # Get chat history
```

## Example Conversation Flow

```
User: "Product Manager"
Bot: Great! What industry or domain are you targeting?

User: "FinTech"
Bot: Perfect! What's your background? (or skip)

User: "skip"
Bot: Any specific interests? (or skip)

User: "skip"
Bot: Let me design a project for you...

    # Payment Flow Optimization Analysis

    You'll analyze payment conversion funnels...
    [Full project proposal]

    What do you think?

User: "yes"
Bot: Now let's define the specific problem...

User: [Provides problem definition]
Bot: [Evaluates problem, provides scores and feedback]

[Continue through solution design, execution, review, resume]
```

## Project Structure

```
MVP/
├── backend/
│   ├── agents/              # AI agents
│   │   ├── project_generator.py
│   │   ├── problem_solution_tutor.py
│   │   ├── execution_coach.py
│   │   ├── reviewer.py
│   │   └── main_chat.py
│   ├── orchestration/       # State machine
│   │   ├── orchestrator.py
│   │   └── state_machine.py
│   ├── schemas/             # Data models
│   ├── modules/             # RAG & Logging
│   └── api/                 # FastAPI endpoints
├── docs/                    # Documentation
├── tests/                   # Tests
├── data/                    # Storage (generated)
└── run.py                   # Start script
```

## Architecture Principles

### 1. State-Based Orchestration
- No agent-to-agent communication
- All coordination through Orchestrator
- Single source of truth

### 2. Explicit I/O
- Clear input/output schemas
- Type-safe communication
- Easy to test and debug

### 3. Single Responsibility
- Each agent has one job
- No overlapping responsibilities
- Clear separation of concerns

## Customization

### Add New State

1. Add to `StateType` enum in `backend/schemas/state.py`
2. Add transition rules in `StateMachine`
3. Implement handler in `Orchestrator`
4. Update `MainChatAgent` for messaging

### Add New Agent

1. Create agent class inheriting from `BaseAgent`
2. Define input/output schemas
3. Implement `process()` method
4. Add to Orchestrator initialization
5. Call from appropriate state handler

### Modify Project Types

Edit `ProjectType` enum and update `ProjectGeneratorAgent` prompts.

### Change Evaluation Criteria

Modify system prompts in `ProblemSolutionTutorAgent`.

## Monitoring

Check logs in `./data/logs/{user_id}/`:
- `state.json` - Current user state
- `transitions.jsonl` - State transition log
- `conversation.jsonl` - Full chat history
- `project_*.json` - Project data
- `problem_*.json` - Problem definitions
- `solution_*.json` - Solution designs
- `milestone_*.json` - Milestone data
- `review_*.json` - Artifact reviews

## Troubleshooting

### "ANTHROPIC_API_KEY is not set"
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Port 8000 already in use
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or change port in run.py
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Slow responses
- Claude API calls take 5-15 seconds
- This is normal for quality AI responses
- Consider adding loading indicators in frontend

## Next Steps

### For Users
1. Complete the full journey with your actual career goals
2. Review generated resume bullets
3. Refine based on feedback
4. Use in job applications!

### For Developers
1. Read `docs/ARCHITECTURE.md` for deep dive
2. Check `docs/API.md` for full API reference
3. See `docs/DEPLOYMENT.md` for production setup
4. Explore `tests/` for testing examples

### For Extending
1. Add database (PostgreSQL) for production
2. Implement user authentication
3. Add frontend (React, Vue, etc.)
4. Create admin dashboard
5. Add payment integration
6. Implement analytics

## Resources

- **Architecture**: `docs/ARCHITECTURE.md`
- **API Docs**: `docs/API.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Interactive API**: `http://localhost:8000/docs`

## Support

For questions or issues:
1. Check documentation in `docs/`
2. Review code comments
3. Inspect logs in `data/logs/`
4. Test with provided examples

## License

[Add your license here]

## Contributors

Built with Claude Sonnet 4.5 following best practices for:
- Multi-agent systems
- State machine architecture
- LLM orchestration
- Production-ready APIs

---

**Ready to build your career-defining project? Start the server and let's go!** 🚀
