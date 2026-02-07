# Frontend Architecture

## Overview

The Sapiens frontend is a single-page application (SPA) built with vanilla HTML, CSS, and JavaScript. It provides a clean, modern chat interface for users to interact with the AI career coach.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              Browser (Client)                    │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │         index.html (Frontend)             │  │
│  │                                           │  │
│  │  ┌─────────────┐  ┌──────────────┐       │  │
│  │  │   Header    │  │  User Input  │       │  │
│  │  │ "Sapiens"   │  │    Field     │       │  │
│  │  └─────────────┘  └──────────────┘       │  │
│  │                                           │  │
│  │  ┌─────────────────────────────┐         │  │
│  │  │    Chat Container           │         │  │
│  │  │  ┌───────────────────────┐  │         │  │
│  │  │  │  User Messages        │  │         │  │
│  │  │  │  (Right-aligned)      │  │         │  │
│  │  │  └───────────────────────┘  │         │  │
│  │  │  ┌───────────────────────┐  │         │  │
│  │  │  │  Bot Messages         │  │         │  │
│  │  │  │  (Left-aligned)       │  │         │  │
│  │  │  └───────────────────────┘  │         │  │
│  │  └─────────────────────────────┘         │  │
│  │                                           │  │
│  │  ┌─────────────────────────────┐         │  │
│  │  │    JavaScript Logic         │         │  │
│  │  │  - sendMessage()            │         │  │
│  │  │  - checkHealth()            │         │  │
│  │  │  - initializeUser()         │         │  │
│  │  │  - addMessage()             │         │  │
│  │  └─────────────────────────────┘         │  │
│  └───────────────┬───────────────────────────┘  │
│                  │ HTTP/REST API                │
└──────────────────┼──────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│              Nginx Reverse Proxy                 │
│              (Port 80)                           │
│                                                  │
│  ┌────────────────┐      ┌──────────────────┐   │
│  │  Static Files  │      │   API Proxy      │   │
│  │  GET /         │      │   POST /api/*    │   │
│  │  → index.html  │      │   → :8000        │   │
│  └────────────────┘      └──────────────────┘   │
└──────────────────┬───────────────┬───────────────┘
                   │               │
                   ▼               ▼
         ┌────────────┐   ┌─────────────────┐
         │  Frontend  │   │  FastAPI        │
         │   Files    │   │  Backend        │
         │            │   │  (Port 8000)    │
         └────────────┘   └─────────────────┘
```

---

## File Structure

```
frontend/
└── index.html          # Single-page application
    ├── <head>          # Styles and metadata
    ├── <body>
    │   ├── Header      # Title and description
    │   ├── Status      # Connection status indicator
    │   ├── User ID     # User identification input
    │   ├── Chat        # Message container
    │   └── Input       # User input and send button
    └── <script>        # Application logic
```

---

## Component Breakdown

### 1. Header Component
```html
<div class="header">
    <h1>🚀 Sapiens</h1>
    <p>Your AI Career Coach for Building Portfolio Projects</p>
</div>
```

**Purpose**: Brand identity and user orientation

**Styling**:
- Gradient background (purple: #667eea → #764ba2)
- Centered text
- White color for contrast

---

### 2. Status Indicator
```html
<div class="status" id="status">Connecting...</div>
```

**States**:
- `Connecting...` - Initial state (gray)
- `✅ Connected to API` - Healthy (green)
- `❌ Cannot connect to API` - Error (red)

**Function**: `checkHealth()`
- Runs on page load
- Fetches `/health` endpoint
- Updates status display

---

### 3. User ID Input
```html
<div class="user-id-container">
    <label>User ID:</label>
    <input type="text" id="user-id" value="">
</div>
```

**Purpose**: User identification and session management

**Auto-generation**:
```javascript
document.getElementById('user-id').value = 'user_' + Math.random().toString(36).substr(2, 9);
```

**Initialization**: `initializeUser(uid)`
- Creates user on first message
- POST to `/api/users?user_id={uid}`

---

### 4. Chat Container
```html
<div class="chat-container" id="chat-container">
    <!-- Messages appear here -->
</div>
```

**Message Structure**:
```html
<div class="message user">
    <div class="message-bubble">User's message</div>
</div>

<div class="message bot">
    <div class="message-bubble">Bot's response</div>
</div>
```

**Styling**:
- User messages: Right-aligned, gradient background
- Bot messages: Left-aligned, white with border
- Auto-scroll to bottom on new messages
- Smooth slide-in animation

---

### 5. Input Component
```html
<div class="input-container">
    <input type="text" id="user-input" placeholder="Type your message here...">
    <button id="send-btn" onclick="sendMessage()">Send</button>
</div>
```

**Features**:
- Enter key to send
- Disabled during processing
- Loading spinner while waiting
- Focus management

---

## JavaScript Architecture

### Core Functions

#### 1. `checkHealth()`
```javascript
async function checkHealth() {
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    // Update status indicator
}
```

**Purpose**: Verify backend connectivity
**Timing**: On page load

---

#### 2. `initializeUser(uid)`
```javascript
async function initializeUser(uid) {
    const response = await fetch(`${API_URL}/api/users?user_id=${uid}`, {
        method: 'POST'
    });
    return response.ok;
}
```

**Purpose**: Create user session
**Timing**: Before first message

---

#### 3. `sendMessage()`
```javascript
async function sendMessage() {
    // 1. Validate user ID
    // 2. Initialize user (first time only)
    // 3. Disable input
    // 4. Add user message to chat
    // 5. Send to API
    // 6. Add bot response to chat
    // 7. Re-enable input
}
```

**Flow**:
```
User types message
       ↓
Click Send / Press Enter
       ↓
Validate user ID
       ↓
Initialize user (if first message)
       ↓
POST /api/chat
       ↓
Display loading spinner
       ↓
Receive response
       ↓
Add bot message to chat
       ↓
Scroll to bottom
       ↓
Re-enable input
```

---

#### 4. `addMessage(text, sender)`
```javascript
function addMessage(text, sender) {
    // 1. Remove welcome message
    // 2. Create message div
    // 3. Add to container
    // 4. Scroll to bottom
}
```

**Purpose**: Render messages in chat
**Animation**: Slide-in from bottom

---

## API Integration

### Configuration
```javascript
const API_URL = 'http://3.101.121.64';  // Nginx proxy
```

### Endpoints Used

#### 1. Health Check
```
GET /health
Response: { "status": "healthy", ... }
```

#### 2. User Initialization
```
POST /api/users?user_id={uid}
Response: { "user_id": "...", "status": "created" }
```

#### 3. Chat
```
POST /api/chat
Body: { "user_id": "...", "message": "..." }
Response: {
    "user_id": "...",
    "response": "...",
    "current_state": "..."
}
```

---

## Styling Architecture

### Color Scheme
```css
Primary Gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Background: #f8f9fa (light gray)
Text: #333 (dark gray)
Border: #e0e0e0 (light gray)
Success: #d4edda (light green)
Error: #f8d7da (light red)
```

### Typography
```css
Font Family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, ...
Header: 2em
Body: 1em (16px base)
Small: 0.85em
```

### Layout
```css
Container: max-width: 800px, height: 90vh
Chat: flex: 1, overflow-y: auto
Messages: max-width: 70% of container
Border Radius: 20px (container), 18px (messages)
```

---

## State Management

### Client-Side State
```javascript
let userId = '';                    // Current user ID
let conversationStarted = false;    // Has user sent first message?
```

### Server-Side State (via API)
- `current_state`: User's state in the workflow
  - `onboarding`
  - `project_generation`
  - `problem_definition`
  - `solution_design`
  - `execution`
  - `review`
  - `completed`

---

## User Experience Flow

```
1. Page Load
   ↓
2. Health Check → Status: "Connected"
   ↓
3. Auto-generate User ID
   ↓
4. User enters message
   ↓
5. Initialize user (POST /api/users)
   ↓
6. Send message (POST /api/chat)
   ↓
7. Display response
   ↓
8. State changes based on conversation
   ↓
9. Repeat steps 4-8
```

---

## Error Handling

### Network Errors
```javascript
try {
    const response = await fetch(...);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
} catch (error) {
    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
}
```

### User Input Validation
```javascript
if (!userId) {
    alert('Please enter a User ID first!');
    return;
}

if (!message) {
    return;  // Don't send empty messages
}
```

---

## Performance Optimizations

### 1. Minimal Dependencies
- No frameworks (React, Vue, etc.)
- Pure HTML/CSS/JavaScript
- Smaller bundle size
- Faster load time

### 2. Efficient Rendering
- Direct DOM manipulation
- No virtual DOM overhead
- Immediate updates

### 3. Loading States
```javascript
userInput.disabled = true;
sendBtn.innerHTML = '<span class="loading"></span>';
```
- Visual feedback during API calls
- Prevents duplicate submissions

### 4. Auto-scroll
```javascript
chatContainer.scrollTop = chatContainer.scrollHeight;
```
- Smooth scroll to latest message
- Better UX for long conversations

---

## Accessibility

### Keyboard Navigation
- Enter key to send messages
- Tab navigation through inputs
- Focus management after send

### Visual Feedback
- Clear loading states
- Disabled states
- Color-coded status indicators

### Semantic HTML
```html
<label>User ID:</label>
<input type="text" ... placeholder="...">
<button onclick="sendMessage()">Send</button>
```

---

## Mobile Responsiveness

### Viewport Meta Tag
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Flexible Layout
```css
.container {
    width: 100%;
    max-width: 800px;
    height: 90vh;
}

.message-bubble {
    max-width: 70%;
    word-wrap: break-word;
}
```

### Touch-Friendly
- Large tap targets (buttons, inputs)
- Readable font sizes
- Adequate spacing

---

## Security Considerations

### XSS Prevention
```javascript
bubble.textContent = text;  // Not .innerHTML
```
- Use `textContent` instead of `innerHTML`
- Prevents script injection

### HTTPS (Production)
- SSL certificates in nginx config
- Redirect HTTP → HTTPS
- Secure cookie flags

### CORS
- Handled by FastAPI backend
- Nginx proxy prevents cross-origin issues

---

## Future Enhancements

### Planned Features
1. **Markdown Rendering** - Rich text in bot responses
2. **File Uploads** - Submit project artifacts
3. **Dark Mode** - User preference toggle
4. **Message History** - Load previous conversations
5. **Typing Indicators** - Show when bot is "thinking"
6. **Audio Messages** - Voice input/output
7. **Multi-language** - i18n support

### Progressive Web App (PWA)
- Service worker for offline support
- Install as native app
- Push notifications

---

## Testing Checklist

### Manual Testing
- [ ] Health check shows "Connected"
- [ ] User ID auto-generates
- [ ] Send button works
- [ ] Enter key sends message
- [ ] Messages display correctly
- [ ] Chat scrolls automatically
- [ ] Loading spinner appears
- [ ] Error messages display
- [ ] Mobile responsive layout

### Browser Compatibility
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (macOS/iOS)
- [ ] Mobile browsers

---

## Deployment

### Build Process
No build required! Pure HTML/CSS/JavaScript.

### Nginx Configuration
```nginx
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
}

location /api/ {
    proxy_pass http://app:8000;
    # ... proxy headers
}
```

### Docker Volume Mount
```yaml
volumes:
  - ./frontend:/usr/share/nginx/html:ro
```

---

## Monitoring & Debugging

### Browser DevTools
```javascript
console.log('User message:', message);
console.log('API response:', data);
console.error('Error:', error);
```

### Network Tab
- Monitor API calls
- Check request/response payloads
- Verify status codes

### Health Endpoint
```bash
curl http://3.101.121.64/health
```

---

## Troubleshooting

### "Cannot connect to API"
1. Check nginx is running: `docker ps`
2. Check health endpoint: `curl http://3.101.121.64/health`
3. Check network/firewall rules

### Messages not sending
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify API_URL is correct
4. Test API directly with curl

### Styling issues
1. Hard refresh (Ctrl+Shift+R)
2. Clear browser cache
3. Check CSS conflicts

---

## Contact & Support

For issues or questions:
- Check logs: `docker logs sapiens_nginx`
- Review backend logs: `docker logs sapiens_app`
- Test API directly with Postman/curl
