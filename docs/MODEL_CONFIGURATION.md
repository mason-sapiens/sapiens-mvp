# Model Configuration Guide

## Current Configuration

The system is now configured to use **OpenAI GPT-4o** as the primary language model.

## Supported Models

### OpenAI Models (Current)

**GPT-4o** (Recommended)
- Model ID: `gpt-4o`
- Best for: Production use, balanced performance and cost
- Pricing: $5/M input tokens, $15/M output tokens
- Context: 128K tokens

**GPT-4 Turbo**
- Model ID: `gpt-4-turbo`
- Best for: High-quality outputs
- Pricing: $10/M input tokens, $30/M output tokens
- Context: 128K tokens

**GPT-4o Mini**
- Model ID: `gpt-4o-mini`
- Best for: Cost optimization
- Pricing: $0.15/M input tokens, $0.60/M output tokens
- Context: 128K tokens

**Future: GPT-5.1**
- When released, simply update `DEFAULT_MODEL=gpt-5.1` in `.env`

## Changing Models

### Quick Change

Edit `.env` file:

```bash
# For GPT-4o (default, recommended)
DEFAULT_MODEL=gpt-4o

# For GPT-4 Turbo (higher quality)
DEFAULT_MODEL=gpt-4-turbo

# For GPT-4o Mini (cost optimization)
DEFAULT_MODEL=gpt-4o-mini

# For future models
DEFAULT_MODEL=gpt-5.1
```

Restart the server:
```bash
python run.py
```

### Per-Agent Model Configuration

You can use different models for different agents based on task complexity:

```python
# In backend/api/main.py

# High-quality agents (use GPT-4o)
self.project_generator = ProjectGeneratorAgent(
    rag_module=rag_module,
    logging_module=logging_module,
    openai_api_key=openai_api_key,
    model="gpt-4o"  # Explicit model
)

# Simple agents (use GPT-4o-mini for cost savings)
self.main_chat = MainChatAgent(
    rag_module=rag_module,
    logging_module=logging_module,
    openai_api_key=openai_api_key,
    model="gpt-4o-mini"  # Cheaper for simple tasks
)
```

## Cost Optimization Strategies

### Strategy 1: Tiered Models

Use different models based on task complexity:

```python
# Complex reasoning: GPT-4o
- ProjectGenerator: gpt-4o
- ProblemSolutionTutor: gpt-4o
- Reviewer: gpt-4o

# Simple tasks: GPT-4o-mini
- MainChat: gpt-4o-mini
- ExecutionCoach: gpt-4o-mini (progress tracking)
```

**Estimated savings: 60-70% on total costs**

### Strategy 2: Token Limits

Reduce `max_tokens` for agents that don't need long responses:

```python
# In specific agent calls
self.call_llm(
    system_prompt=prompt,
    user_prompt=message,
    max_tokens=1000,  # Lower for shorter responses
    temperature=0.7
)
```

### Strategy 3: Caching

Implement response caching for repeated queries:

```python
import hashlib
import json

def get_cached_response(prompt_hash):
    # Check Redis/database for cached response
    pass

def call_llm_with_cache(system_prompt, user_prompt):
    # Hash the prompts
    prompt_hash = hashlib.md5(
        f"{system_prompt}{user_prompt}".encode()
    ).hexdigest()

    # Check cache
    cached = get_cached_response(prompt_hash)
    if cached:
        return cached

    # Call API and cache result
    response = self.call_llm(system_prompt, user_prompt)
    cache_response(prompt_hash, response)
    return response
```

## Switching Back to Anthropic Claude

If you want to use Claude instead:

### 1. Update Environment

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEFAULT_MODEL=claude-sonnet-4-5-20250929
```

### 2. Update Base Agent

```python
# backend/agents/base.py
from anthropic import Anthropic

def __init__(self, ..., anthropic_api_key: Optional[str] = None,
             model: str = "claude-sonnet-4-5-20250929"):
    api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
    self.client = Anthropic(api_key=api_key)
    self.model = model

def call_llm(self, system_prompt: str, user_prompt: str, ...):
    message = self.client.messages.create(
        model=self.model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return message.content[0].text
```

### 3. Update Requirements

```bash
pip install anthropic
```

## Model Comparison

| Model | Cost per Journey | Quality | Speed | Best For |
|-------|-----------------|---------|-------|----------|
| GPT-4o | ~$0.15-0.45 | Excellent | Fast | Production (recommended) |
| GPT-4 Turbo | ~$0.30-0.90 | Excellent | Fast | High-quality outputs |
| GPT-4o Mini | ~$0.01-0.03 | Good | Very Fast | Cost optimization |
| Claude Sonnet 4.5 | ~$0.10-0.30 | Excellent | Fast | Alternative (if preferred) |

## Testing Different Models

Use environment variables to test different models without code changes:

```bash
# Test GPT-4o
DEFAULT_MODEL=gpt-4o python run.py

# Test GPT-4o-mini
DEFAULT_MODEL=gpt-4o-mini python run.py

# Compare outputs
```

## Model-Specific Considerations

### GPT-4o
- **Strengths**: Best balance of cost, quality, and speed
- **Best for**: Production deployment
- **Watch out for**: None, well-balanced

### GPT-4o Mini
- **Strengths**: Very low cost
- **Best for**: High-volume, simple tasks
- **Watch out for**: May produce lower quality on complex reasoning tasks

### GPT-4 Turbo
- **Strengths**: Highest quality outputs
- **Best for**: Premium tier users, critical evaluations
- **Watch out for**: Higher cost

## Monitoring Model Performance

Track these metrics per model:

```python
# Add to logging
metrics = {
    "model": self.model,
    "tokens_used": response.usage.total_tokens,
    "cost": calculate_cost(response.usage),
    "latency": time.time() - start_time,
    "agent": self.agent_name
}
```

## Future-Proofing

The system is designed to easily adopt new models:

1. **GPT-5** (when released):
   ```bash
   DEFAULT_MODEL=gpt-5
   ```

2. **Other providers** (Cohere, etc.):
   - Update `BaseAgent.call_llm()` method
   - Add API client initialization
   - Update environment variables

## Troubleshooting

### "Model not found" error

Make sure the model ID is correct:
```python
# Correct
DEFAULT_MODEL=gpt-4o

# Incorrect
DEFAULT_MODEL=gpt4o  # Missing hyphen
DEFAULT_MODEL=GPT-4o  # Wrong case
```

### High costs

1. Check model being used: `echo $DEFAULT_MODEL`
2. Review `max_tokens` settings
3. Consider switching to GPT-4o-mini for appropriate agents
4. Implement caching

### Slow responses

1. Check model latency (GPT-4o-mini is fastest)
2. Reduce `max_tokens` if applicable
3. Use async processing for non-critical paths

## Best Practices

1. **Use GPT-4o for production** - Best balance
2. **Test thoroughly** when changing models - Output format may vary
3. **Monitor costs** - Set up billing alerts
4. **Keep prompts model-agnostic** - Avoid model-specific instructions
5. **Log model versions** - Track which model generated which output

## Getting API Keys

### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Create account
3. Generate API key
4. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Anthropic (if switching back)
1. Visit https://console.anthropic.com/
2. Create account
3. Generate API key
4. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

## Questions?

- OpenAI Models: https://platform.openai.com/docs/models
- Pricing: https://openai.com/api/pricing/
- Rate Limits: https://platform.openai.com/docs/guides/rate-limits
