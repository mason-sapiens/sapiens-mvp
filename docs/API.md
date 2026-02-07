# Sapiens MVP API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (MVP). Production will use JWT tokens.

## Endpoints

### Health Check

#### `GET /health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

### Create User

#### `POST /api/users`

Create a new user session.

**Parameters:**
- `user_id` (query): Unique user identifier

**Response:**
```json
{
  "user_id": "usr_123",
  "status": "created"
}
```

---

### Send Message

#### `POST /api/chat`

Main endpoint for sending messages to the system.

**Request Body:**
```json
{
  "user_id": "usr_123",
  "message": "I want to be a Product Manager"
}
```

**Response:**
```json
{
  "user_id": "usr_123",
  "response": "Welcome to Sapiens! I'm here to guide you...",
  "current_state": "onboarding"
}
```

**States:**
- `onboarding`: Collecting user profile
- `project_generation`: Creating project proposal
- `problem_definition`: Defining problem
- `solution_design`: Designing solution
- `execution`: Working on milestones
- `review`: Reviewing artifacts
- `completed`: Journey complete

---

### Get User State

#### `GET /api/state/{user_id}`

Get current state of a user.

**Response:**
```json
{
  "user_id": "usr_123",
  "current_state": "problem_definition",
  "state_entered_at": "2024-01-15T10:30:00",
  "context": {
    "problem_submitted": true,
    "awaiting_feedback": true
  }
}
```

---

### Get Project

#### `GET /api/project/{user_id}`

Get user's project details.

**Response:**
```json
{
  "project_id": "proj_abc",
  "user_id": "usr_123",
  "proposal": {
    "title": "Payment Flow Optimization Analysis",
    "project_type": "research",
    "description": "...",
    "deliverables": [...],
    "skills_demonstrated": [...]
  },
  "status": "active"
}
```

---

### Get Conversation History

#### `GET /api/conversation/{user_id}`

Get conversation history for a user.

**Parameters:**
- `limit` (query, optional): Number of messages to return (default: 50)

**Response:**
```json
{
  "user_id": "usr_123",
  "history": [
    {
      "timestamp": "2024-01-15T10:00:00",
      "type": "user_message",
      "message": "I want to be a PM",
      "metadata": {}
    },
    {
      "timestamp": "2024-01-15T10:00:01",
      "type": "agent_response",
      "agent": "MainChat",
      "response": "Great! ...",
      "metadata": {}
    }
  ]
}
```

---

## Usage Examples

### Complete Onboarding Flow

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "usr_demo_001"

# 1. Create user
requests.post(f"{BASE_URL}/api/users?user_id={USER_ID}")

# 2. Start conversation
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "user_id": USER_ID,
        "message": "Product Manager"
    }
)
print(response.json()["response"])

# 3. Provide domain
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "user_id": USER_ID,
        "message": "FinTech"
    }
)
print(response.json()["response"])

# 4. Skip optional fields
for _ in range(2):
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "user_id": USER_ID,
            "message": "skip"
        }
    )
    print(response.json()["response"])

# 5. Check state
state = requests.get(f"{BASE_URL}/api/state/{USER_ID}")
print(f"Current state: {state.json()['current_state']}")

# 6. Get project
project = requests.get(f"{BASE_URL}/api/project/{USER_ID}")
print(f"Project: {project.json()['proposal']['title']}")
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = "http://localhost:8000";
const USER_ID = "usr_demo_002";

async function chat(message: string) {
  const response = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: USER_ID,
      message: message,
    }),
  });

  const data = await response.json();
  return data.response;
}

// Usage
const response = await chat("I want to be a Data Scientist");
console.log(response);
```

### cURL Examples

```bash
# Create user
curl -X POST "http://localhost:8000/api/users?user_id=usr_demo_003"

# Send message
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_demo_003",
    "message": "Marketing Manager"
  }'

# Get state
curl "http://localhost:8000/api/state/usr_demo_003"

# Get project
curl "http://localhost:8000/api/project/usr_demo_003"

# Get conversation
curl "http://localhost:8000/api/conversation/usr_demo_003?limit=20"
```

## Error Responses

All errors return a JSON object with a `detail` field:

```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

- `200 OK`: Success
- `404 Not Found`: Resource not found (user, project, etc.)
- `500 Internal Server Error`: Server error

## WebSocket Support (Future)

Future versions will include WebSocket support for real-time streaming responses:

```
ws://localhost:8000/ws/chat/{user_id}
```

## Rate Limiting (Future)

Production API will include rate limiting:
- 100 requests per minute per user
- 1000 requests per hour per user

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints.
