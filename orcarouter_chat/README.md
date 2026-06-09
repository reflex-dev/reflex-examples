# OrcaRouter chat

A minimal Reflex chat app that calls [OrcaRouter](https://www.orcarouter.ai),
an OpenAI-compatible LLM gateway, and lets you switch between adaptive routing
(`orcarouter/auto`) and specific upstream models from a dropdown -- same API
key, same endpoint.

The model dropdown is populated at startup from OrcaRouter's public pricing
catalog (`https://www.orcarouter.ai/api/pricing`, no auth required), so new
models added on the server side show up the next time you click **Refresh**.
If the catalog endpoint is unreachable the app falls back to a curated list of
flagship models.

## Setup

1. Get an API key at <https://www.orcarouter.ai/console> (the key starts with
   `sk-orca-`).
2. Copy the example env file and paste your key:
   ```bash
   cp .env.example .env
   # then edit .env and set ORCAROUTER_API_KEY=sk-orca-...
   ```
3. Install dependencies and run:
   ```bash
   pip install -r requirements.txt
   reflex run
   ```

Open <http://localhost:3000>, pick a model from the dropdown, and start
chatting.

## What this example demonstrates

- Using OrcaRouter as a drop-in OpenAI-compatible provider
  (`AsyncOpenAI(base_url="https://api.orcarouter.ai/v1", api_key=...)`).
- Switching between `orcarouter/auto` (adaptive routing) and specific upstream
  models (`openai/...`, `anthropic/...`, ...) without changing client code.
- Passing OrcaRouter-specific routing preferences via the `extra_body` field
  (`{"models": [...], "route": "fallback"}`).
- Attaching attribution headers (`HTTP-Referer`, `X-Title`) so OrcaRouter can
  report which client originated the request.
- Skipping `temperature` for reasoning models (Claude Opus, GPT-5 family,
  DeepSeek reasoner) which reject the parameter.

## References

- OrcaRouter docs: <https://docs.orcarouter.ai>
- Routing strategies and `orcarouter/auto`:
  <https://www.orcarouter.ai/console/routing>
- Full model catalog: <https://www.orcarouter.ai/models>
