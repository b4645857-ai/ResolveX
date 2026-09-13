# ResolveX — Autonomous Customer Resolution Agent

Round 1 — Tech Zephyr 4.0 / IIT Bhubaneswar / Problem Statement 5.

ResolveX is a web-based agentic customer-resolution prototype. It investigates a case through simulated enterprise tools, selects a resolution, executes a state-changing action, observes the result, adapts when a constraint blocks the first plan, and verifies the final state.

## Agentic workflow
Goal → Decision → Action → Intermediate Result → Adaptation → Final Outcome.

## Main demo
CUST-1042 / ORD-7712: damaged laptop. Replacement inventory is intentionally zero. The agent discovers the constraint and adapts to an eligible refund, then verifies the order state.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# add your OpenAI API key to .env
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000

The app includes a state-aware deterministic fallback so the demo can still run without an API key. With an OpenAI key, the agent attempts model-driven next-action selection and falls back safely if the API is unavailable.

## Security
Never commit `.env` or API keys. The enterprise systems are synthetic and sandboxed.
