# CKCIAS Sidecar - Updated Multi-Model Architecture Plan

## Overview
High-performance sidecar service handling 95% of LLM requests with intelligent load balancing across multiple AI providers.

---

## Supported Models (2025)

### 1. Anthropic Claude (Primary - High Quality Tasks)
- **Sonnet 4.5** (Complex reasoning, coding, agents)
  - Model: `claude-sonnet-4-5-20250929`
  - Alias: `claude-sonnet-4-5`
  - Rate Limit: 50 RPM, 40,000 TPM
  - Cost: $3/M input, $15/M output
  - Use Case: Complex analysis, multi-step reasoning, coding tasks

- **Haiku 4.5** (Fast, cost-effective)
  - Model: `claude-haiku-4-5`
  - Specific: `claude-haiku-4-5-20251015`
  - Rate Limit: 50 RPM, 50,000 TPM
  - Cost: $1/M input, $5/M output
  - Context: 200K tokens, 64K output
  - Use Case: Quick responses, simple queries, high-volume tasks

### 2. Groq API (Ultra-Fast Inference)
- **Kimi K2** (256K context, agentic coding)
  - Model: `moonshotai/kimi-k2-instruct-0905`
  - Context: 256K tokens
  - Architecture: 1T total params, 32B active (MoE)
  - Rate Limit: TBD (check Groq dashboard)
  - Use Case: Large context tasks, code analysis

- **Llama 3.3 70B Versatile**
  - Model: `llama-3.3-70b-versatile`
  - Parameters: 70B
  - Rate Limit: TBD (check Groq dashboard)
  - Use Case: General-purpose, multilingual tasks

### 3. Google Gemini (Backup/Specialized)
- **Gemini 2.5 Flash**
  - Model: `gemini-2.5-flash`
  - Rate Limit: 200 RPM, 2M TPM
  - Cost: Low
  - Use Case: Backup provider, multimodal tasks

---

## Task Routing Strategy

### Automatic Model Selection Logic

```python
def select_model(request):
    """Intelligent model selection based on task complexity and cost"""

    # High complexity tasks → Sonnet 4.5
    if request.complexity == 'high' or request.task_type in ['coding', 'reasoning', 'agents']:
        return 'claude-sonnet-4-5'

    # Large context needs → Kimi K2 (256K context)
    if request.context_length > 100000:
        return 'moonshotai/kimi-k2-instruct-0905'

    # Fast, simple queries → Haiku 4.5 or Groq Llama
    if request.priority == 'speed':
        return 'llama-3.3-70b-versatile'  # Groq ultra-fast

    # Cost-optimized → Haiku 4.5
    if request.priority == 'cost':
        return 'claude-haiku-4-5'

    # Default → Haiku 4.5 (best balance)
    return 'claude-haiku-4-5'
```

### Task Type Mapping

| Task Type | Primary Model | Fallback |
|-----------|---------------|----------|
| Complex Reasoning | Sonnet 4.5 | Kimi K2 |
| Coding | Sonnet 4.5 | Kimi K2 |
| Agent Workflows | Sonnet 4.5 | Haiku 4.5 |
| Quick Queries | Haiku 4.5 | Llama 70B |
| Large Context (>100K) | Kimi K2 | Sonnet 4.5 |
| Speed Critical | Llama 70B (Groq) | Haiku 4.5 |
| Cost Critical | Haiku 4.5 | Llama 70B |
| Multimodal | Gemini 2.5 Flash | Sonnet 4.5 |

---

## Rate Limiting Configuration

### Per-Provider Limits

```python
RATE_LIMITS = {
    'anthropic': {
        'rpm': 50,  # Requests per minute
        'tpm': 50000,  # Tokens per minute (Haiku)
        'buffer': 0.1  # 10% safety buffer
    },
    'groq': {
        'rpm': 100,  # Check actual limits
        'tpm': 50000,  # Estimated
        'buffer': 0.1
    },
    'gemini': {
        'rpm': 200,
        'tpm': 2000000,
        'buffer': 0.1
    }
}
```

### Load Balancing Strategy

1. **Token Bucket Algorithm** - Smooth rate limiting
2. **Round Robin** - Distribute across providers
3. **Weighted Selection** - Based on current load and latency
4. **Automatic Failover** - If one provider is rate-limited

---

## Architecture Components

### 1. Request Router
```python
class RequestRouter:
    def __init__(self):
        self.providers = {
            'anthropic': AnthropicProvider(),
            'groq': GroqProvider(),
            'gemini': GeminiProvider()
        }
        self.rate_limiter = RateLimiter()

    async def route(self, request):
        model = self.select_model(request)
        provider = self.get_provider(model)

        # Check rate limits
        if not self.rate_limiter.allow(provider):
            # Failover to alternative
            provider = self.get_fallback_provider(model)

        return await provider.process(request)
```

### 2. Provider Adapters

```python
class AnthropicProvider:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.models = {
            'sonnet': 'claude-sonnet-4-5-20250929',
            'haiku': 'claude-haiku-4-5'
        }

    async def process(self, request):
        response = await self.client.messages.create(
            model=self.models[request.model_tier],
            max_tokens=request.max_tokens,
            messages=request.messages
        )
        return response
```

```python
class GroqProvider:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.models = {
            'kimi': 'moonshotai/kimi-k2-instruct-0905',
            'llama': 'llama-3.3-70b-versatile'
        }

    async def process(self, request):
        response = await self.client.chat.completions.create(
            model=self.models[request.model_tier],
            messages=request.messages
        )
        return response
```

### 3. Worker Pool

```python
class WorkerPool:
    def __init__(self, num_workers=10):
        self.workers = []
        self.request_queue = asyncio.Queue()

        for i in range(num_workers):
            worker = Worker(
                worker_id=i,
                router=RequestRouter(),
                queue=self.request_queue
            )
            self.workers.append(worker)

    async def start(self):
        tasks = [worker.run() for worker in self.workers]
        await asyncio.gather(*tasks)
```

---

## Performance Optimization

### 1. Connection Pooling
- Maintain 20 persistent connections per provider
- Reduce connection overhead
- HTTP/2 multiplexing where supported

### 2. Request Batching
- Group similar requests (same model, similar context)
- Batch size: 5-10 requests
- Max wait time: 500ms

### 3. Caching
- Cache frequent queries (LRU strategy)
- TTL: 1 hour for static responses
- Skip caching for user-specific data

### 4. Streaming Responses
- Use SSE (Server-Sent Events) for real-time streaming
- Reduce perceived latency
- Better UX for long responses

---

## Cost Optimization

### Monthly Cost Estimates (at scale)

| Model | Cost per 1M requests | Use Case |
|-------|---------------------|----------|
| Haiku 4.5 | ~$100 (avg 1K tokens I/O) | 70% of requests |
| Sonnet 4.5 | ~$300 (avg 2K tokens I/O) | 20% of requests |
| Groq Llama | ~$0 (free tier) | 5% of requests |
| Kimi K2 | ~$50 | 5% of requests |

**Total estimated: ~$450/month for 1M requests**

### Cost-Saving Strategies
1. **Tiered Routing**: Use cheapest model that meets requirements
2. **Caching**: Reduce duplicate API calls by 30-40%
3. **Groq Free Tier**: Maximize usage for speed-critical tasks
4. **Haiku First**: Default to Haiku 4.5 unless complexity requires Sonnet

---

## Monitoring & Metrics

### Key Metrics Dashboard
- Request latency per model (p50, p95, p99)
- Rate limit utilization (%)
- Cost per request
- Error rates by provider
- Cache hit rate
- Queue depth and wait time

### Health Checks
```python
health_endpoints = {
    'anthropic': 'https://api.anthropic.com/v1/messages',
    'groq': 'https://api.groq.com/openai/v1/models',
    'gemini': 'https://generativelanguage.googleapis.com/v1/models'
}
```

### Alerting Rules
- Rate limit > 80% → Switch to fallback provider
- Error rate > 5% → Alert DevOps
- Latency p95 > 5s → Investigate slow provider
- Cost spike > 20% → Review routing logic

---

## Deployment Options

### Option 1: Local Development (Recommended Start)
```bash
# WSL/Linux
python sidecar.py --workers 10 --port 8001
```

### Option 2: Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "sidecar.py"]
```

### Option 3: Cloud (Production)
- **AWS Lambda** + API Gateway (serverless)
- **GCP Cloud Run** (auto-scaling)
- **Azure Container Apps**

---

## Integration with CKCIAS Drought Monitor

### Update Frontend API Service
```typescript
// services/api.ts
const SIDECAR_URL = 'http://localhost:8001';

export const sendChatMessage = async (message: string): Promise<string> => {
  try {
    const res = await fetch(`${SIDECAR_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: message }],
        model_preference: 'auto',  // Let sidecar choose
        task_type: 'drought_analysis'
      })
    });
    return (await res.json()).response;
  } catch (error) {
    // Fallback to direct Gemini call
    return fallbackGemini(message);
  }
};
```

### Update Backend Routes
```python
# backend/routes.py
SIDECAR_URL = 'http://localhost:8001'

@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Proxy to sidecar for LLM requests"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SIDECAR_URL}/chat",
            json={
                "messages": [{"role": "user", "content": request.message}],
                "model_preference": "haiku",  # Default to Haiku for cost
                "task_type": "drought_analysis"
            }
        )
        return response.json()
```

---

## Next Steps

1. ✅ Research latest model names
2. ⏳ Create `.env` file with API keys
3. ⏳ Build sidecar service (`sidecar.py`)
4. ⏳ Create provider adapters
5. ⏳ Implement rate limiting
6. ⏳ Add monitoring dashboard
7. ⏳ Test with CKCIAS app
8. ⏳ Deploy to production

---

## Expected Performance

- **95% of LLM requests** handled by sidecar
- **Average latency**: <2s (Groq), <3s (others)
- **Cost reduction**: 60% vs using only Sonnet
- **Uptime**: 99.9% (with failover)
- **Throughput**: 1000+ requests/minute

This architecture provides optimal balance of speed, cost, and quality!
