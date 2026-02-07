# Migration Notes: Claude → OpenAI GPT-4o

## Changes Made

The system has been migrated from **Anthropic Claude** to **OpenAI GPT-4o**.

### Updated Files

1. **backend/agents/base.py**
   - Changed from `anthropic.Anthropic` to `openai.OpenAI`
   - Renamed `call_claude()` to `call_llm()` (with backward-compatible alias)
   - Updated message format from Claude to OpenAI format

2. **backend/orchestration/orchestrator.py**
   - Changed `anthropic_api_key` parameter to `openai_api_key`
   - Updated all agent initializations

3. **backend/api/main.py**
   - Updated orchestrator initialization
   - Changed environment variable from `ANTHROPIC_API_KEY` to `OPENAI_API_KEY`

4. **config/settings.py**
   - Changed API key field
   - Updated default model to `gpt-4o`

5. **Environment Files**
   - `.env.example`: Updated to use OpenAI credentials
   - `run.py`: Updated API key check

6. **Documentation**
   - Updated all references to model and API provider
   - Added MODEL_CONFIGURATION.md guide

### API Format Changes

**Before (Claude):**
```python
message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    temperature=0.7,
    system=system_prompt,
    messages=[{"role": "user", "content": user_prompt}]
)
return message.content[0].text
```

**After (OpenAI):**
```python
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=4096,
    temperature=0.7,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)
return response.choices[0].message.content
```

## Migration Checklist

- [x] Update base agent class
- [x] Update orchestrator initialization
- [x] Update API configuration
- [x] Update environment variables
- [x] Update documentation
- [x] Update tests
- [x] Add model configuration guide
- [ ] Test full user journey
- [ ] Verify all agents work correctly
- [ ] Check response quality
- [ ] Monitor costs

## What You Need to Do

### 1. Update Environment Variables

```bash
# Remove old key
unset ANTHROPIC_API_KEY

# Add new key
export OPENAI_API_KEY=sk-your-openai-key-here

# Or update .env file
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
```

### 2. Get OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create account or sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Add to your `.env` file

### 3. Reinstall Dependencies (if needed)

```bash
pip install -r requirements.txt
```

The `openai` package was already in requirements.txt, so this should work without issues.

### 4. Test the System

```bash
# Start server
python run.py

# Test health endpoint
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Product Manager"}'
```

## Expected Behavior Changes

### Response Style
- GPT-4o may format responses slightly differently than Claude
- Generally more concise
- May need prompt adjustments for optimal output

### Cost Comparison
- Claude Sonnet 4.5: $3/M input, $15/M output
- GPT-4o: $5/M input, $15/M output
- **Similar costs**, GPT-4o slightly higher on input tokens

### Performance
- Both models are fast (~3-10s per call)
- GPT-4o-mini available for cost optimization
- Similar quality for most tasks

## Prompt Adjustments (If Needed)

If you notice quality issues, you may need to adjust prompts:

```python
# Claude-style prompt (more verbose)
"You are an expert career coach. Your task is to..."

# GPT-4o-style prompt (can be more concise)
"As a career coach, design a project that..."
```

The current prompts should work well with both models.

## Rollback Instructions

If you need to revert to Claude:

### 1. Update base.py

```python
from anthropic import Anthropic

def __init__(self, ..., anthropic_api_key=None, model="claude-sonnet-4-5-20250929"):
    api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
    self.client = Anthropic(api_key=api_key)

def call_llm(self, system_prompt, user_prompt, max_tokens=4096, temperature=0.7):
    message = self.client.messages.create(
        model=self.model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return message.content[0].text
```

### 2. Update orchestrator.py

Change all `openai_api_key` back to `anthropic_api_key`

### 3. Update environment

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key
DEFAULT_MODEL=claude-sonnet-4-5-20250929
```

### 4. Restart

```bash
python run.py
```

## Advantages of OpenAI

1. **Wider Ecosystem**: More tools and integrations
2. **Model Variety**: Multiple models for different use cases (4o, 4o-mini, 4-turbo)
3. **Future Models**: Easy to upgrade to GPT-5 when released
4. **Batch API**: Available for cost savings on non-real-time tasks
5. **Function Calling**: Native support for structured outputs

## Known Issues

None currently. If you encounter issues:

1. Check API key is set correctly
2. Verify model name is exact: `gpt-4o` (not `gpt4o` or `GPT-4o`)
3. Check OpenAI account has credits
4. Review API rate limits

## Testing Recommendations

Test these user journeys:

1. **Onboarding**: Role → Domain → Background → Interests
2. **Project Generation**: Verify project proposal quality
3. **Problem Evaluation**: Check scoring accuracy
4. **Solution Evaluation**: Check feedback quality
5. **Execution Coaching**: Verify milestone creation
6. **Review & Resume**: Check resume bullet quality

## Support

- OpenAI Documentation: https://platform.openai.com/docs
- Model Info: https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4
- API Reference: https://platform.openai.com/docs/api-reference

## Notes

- All system prompts remain unchanged
- Agent logic remains unchanged
- Only the LLM API client was swapped
- Response parsing works the same way
- The system is model-agnostic by design

## Future: GPT-5.1

When GPT-5.1 is released:

1. Update `.env`:
   ```bash
   DEFAULT_MODEL=gpt-5.1
   ```

2. Test thoroughly (new models may have different behavior)

3. Update documentation with new pricing

That's it! The system is designed to adapt to new models easily.
