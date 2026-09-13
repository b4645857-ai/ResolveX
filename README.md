# ResolveX — Autonomous Customer Resolution Agent

> **Tech Zephyr 4.0 · IIT Bhubaneswar · Problem Statement 5 — Smart Automation**

ResolveX is an autonomous AI-powered customer resolution agent that does more than generate a response.

It investigates customer and order information, consults resolution policies, checks simulated inventory, selects and executes an appropriate resolution, observes the result, adapts when its original plan is blocked, and verifies that the final enterprise state reflects the intended outcome.

---

## 🚀 Live Demo

**Live Application:**  
https://resolvex-qj8k.onrender.com/

**GitHub Repository:**  
https://github.com/b4645857-ai/ResolveX

---

# 🎯 Problem

Traditional customer-support systems often stop at:

> "Based on our policy, you are eligible for a replacement."

That is not resolution.

A real resolution agent needs to determine what can actually be done in the current enterprise environment and then take the necessary action.

For example, a customer may request a replacement for a damaged laptop. The replacement may be allowed by policy, but the required product may currently be out of stock.

A useful autonomous agent should:

1. Investigate the case.
2. Determine customer and order eligibility.
3. Check the current inventory.
4. Detect when the original plan cannot be executed.
5. Replan using an eligible alternative.
6. Execute the alternative.
7. Verify that the enterprise state actually changed.

ResolveX is designed around this workflow.

---

# 🧠 What ResolveX Does

ResolveX follows an autonomous decision loop:

```text
GOAL
  ↓
OBSERVE
  ↓
DECIDE
  ↓
ACT
  ↓
RESULT
  ↓
ADAPT
  ↓
VERIFY
```

The system interacts with a simulated enterprise environment and uses intermediate results to determine what to do next.

Unlike a one-shot chatbot, ResolveX is designed to pursue a resolution objective through tool interaction, environmental feedback, adaptive planning, and final verification.

---

# 🔄 Agentic Workflow

## 1. Goal

The agent receives a customer issue such as:

> "My laptop arrived damaged. I want a replacement."

The goal is to resolve the customer's case using the available enterprise systems and permitted policies.

---

## 2. Observe

The agent investigates the current environment using tools.

It can query:

- Customer information
- Order information
- Resolution policy
- Inventory availability

Example:

```text
Customer Lookup
      ↓
Order Lookup
      ↓
Policy Lookup
      ↓
Inventory Check
```

The agent builds the necessary case state before taking a resolution action.

---

## 3. Decide

Based on the observed state, the agent determines the next appropriate action.

For example:

```text
Replacement requested
        +
Replacement permitted by policy
        ↓
Check replacement inventory
```

The agent does not assume that the requested action can be executed.

---

## 4. Act

When the required conditions are satisfied, ResolveX executes an action through the simulated enterprise tools.

Supported resolution actions include:

- Replacement creation
- Refund processing

The action modifies the simulated enterprise state.

---

## 5. Observe the Result

After interacting with the environment, the agent evaluates the result.

For example:

```text
Replacement request
        ↓
Inventory API
        ↓
Available units = 0
        ↓
OUT_OF_STOCK
```

The original plan is now blocked by the environment.

---

## 6. Adapt

This is the key agentic behavior demonstrated by ResolveX.

The agent does not repeatedly attempt the failed action.

Instead, it reevaluates the available options.

Example:

```text
Replacement unavailable
        ↓
Check policy
        ↓
Refund permitted
        ↓
Select refund
```

The agent therefore adapts its plan based on an intermediate environmental result.

---

## 7. Verify

After executing the resolution, ResolveX calls a verification tool.

It checks the resulting enterprise state rather than assuming that the action succeeded.

Example:

```text
Refund processed
        ↓
Verify Resolution
        ↓
Order status = Refund processed
        ↓
Resolution VERIFIED
```

Only after successful verification does the system present the case as resolved.

---

# 🧪 Demonstration Scenarios

ResolveX contains two simulated customer cases designed to demonstrate different autonomous behaviors.

---

## Scenario 1 — Damaged Laptop / Replacement Unavailable

```text
Customer: CUST-1042
Order:    ORD-7712
Product:  NovaBook Pro 14
Issue:    Arrived damaged
```

The customer requests a replacement.

The policy permits both replacement and refund.

However:

```text
Replacement SKU: NBP14-2026
Inventory:       0 units
```

The replacement cannot be executed.

ResolveX detects the environmental constraint and adapts:

```text
Replacement requested
        ↓
Policy permits replacement
        ↓
Inventory = 0
        ↓
ADAPT
        ↓
Refund selected
        ↓
Refund processed
        ↓
Verification
        ↓
RESOLVED
```

### Why this scenario matters

This demonstrates that the agent:

- Investigates the environment.
- Detects an execution constraint.
- Does not blindly repeat a failed action.
- Selects an eligible alternative.
- Executes the alternative.
- Verifies the resulting state.

---

## Scenario 2 — Wrong Color / Replacement Available

```text
Customer: CUST-2048
Order:    ORD-8821
Product:  PulseBuds X
Issue:    Wrong color
```

The customer requests the correct product.

The replacement is permitted and inventory is available:

```text
Replacement SKU: PBX-BLK
Inventory:       12 units
```

ResolveX therefore executes the replacement path:

```text
Customer lookup
        ↓
Order lookup
        ↓
Policy lookup
        ↓
Inventory check
        ↓
Replacement available
        ↓
Create replacement
        ↓
Verify resolution
        ↓
RESOLVED
```

This demonstrates that the agent does not blindly choose a refund and instead selects the appropriate action based on the current state.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      Customer        │
                         │       Issue          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     ResolveX Agent   │
                         │                      │
                         │ Goal → Observe       │
                         │ → Decide → Act       │
                         │ → Result → Adapt    │
                         │ → Verify             │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │   Customer   │      │    Order     │      │    Policy    │
      │    Lookup    │      │    Lookup    │      │    Lookup    │
      └──────────────┘      └──────────────┘      └──────────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │  Inventory   │
                            │    Check     │
                            └──────┬───────┘
                                   │
                       ┌───────────┴───────────┐
                       │                       │
                 Available                 Unavailable
                       │                       │
                       ▼                       ▼
                Replacement                 Adapt
                       │                       │
                       │                       ▼
                       │                    Refund
                       │                       │
                       └───────────┬───────────┘
                                   ▼
                           ┌──────────────┐
                           │ Verification │
                           └──────┬───────┘
                                  ▼
                           Final Resolution
```

---

# 🛠️ Technology Stack

## Backend

- Python
- FastAPI
- OpenAI Responses API
- Pydantic

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript

## AI

- OpenAI GPT-5.6 Luna
- Function/tool calling
- Autonomous tool selection
- State-aware decision making

## Simulated Enterprise Systems

ResolveX implements simulated enterprise tools for:

- Customer lookup
- Order lookup
- Policy lookup
- Inventory lookup
- Replacement creation
- Refund processing
- Resolution verification

---

# 📁 Project Structure

```text
ResolveX/
│
├── backend/
│   ├── __init__.py
│   ├── agent.py
│   ├── main.py
│   └── simulated_systems.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── data/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# ⚙️ How It Works

## Backend

`backend/main.py`

Provides the FastAPI application and HTTP endpoints used by the frontend.

Main endpoints:

```text
GET  /              → Web application
GET  /api/cases     → Available demo cases
POST /api/resolve   → Run autonomous resolution
```

---

## Agent

`backend/agent.py`

Contains the ResolveX agent workflow.

The agent:

1. Receives the customer goal.
2. Determines which enterprise information is required.
3. Calls the appropriate tools.
4. Receives intermediate results.
5. Chooses the next action.
6. Executes state-changing operations when permitted.
7. Adapts when an action is blocked.
8. Calls verification.
9. Produces the final resolution result and execution trace.

---

## Simulated Enterprise Environment

`backend/simulated_systems.py`

Contains the simulated enterprise state and tool implementations.

The environment maintains:

```text
Customers
Orders
Policies
Inventory
Refunds
Replacements
```

Actions such as refunds and replacements update the simulated state.

This makes it possible to demonstrate that the agent is interacting with an environment rather than simply generating a text response.

---

# 🔐 Safety / Sandbox

ResolveX is intentionally implemented as a simulated enterprise environment.

The prototype does not modify:

- Real customers
- Real orders
- Real payments
- Real inventory
- Real enterprise systems

All state changes occur inside the simulated environment.

API credentials are stored through environment variables and are not committed to source control.

---

# 🚀 Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/b4645857-ai/ResolveX.git
cd ResolveX
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file in the project root.

Use:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna
```

Never commit `.env` to GitHub.

---

## 5. Run the application

```bash
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

# 🌐 Production Deployment

ResolveX is deployed as a FastAPI web service.

**Live deployment:**

https://resolvex-qj8k.onrender.com/

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Required Environment Variables

```text
OPENAI_API_KEY
OPENAI_MODEL
```

The API key is configured through the hosting provider's environment-variable system and is not stored in the GitHub repository.

---

# 🎬 Recommended Demo Flow

For the strongest demonstration, use:

**Damaged laptop · replacement unavailable**

Start with:

```text
Customer Issue:

"My laptop arrived damaged. I want a replacement."
```

Then run the agent.

Highlight these moments:

### 1. Goal

The customer wants a replacement.

### 2. Observe

The agent investigates:

```text
Customer
Order
Policy
Inventory
```

### 3. Decision

Replacement is permitted, so the agent checks whether it can actually be fulfilled.

### 4. Intermediate Result

Inventory returns:

```text
0 units
```

### 5. Adaptation

The replacement path is blocked.

ResolveX evaluates the available policy options and chooses a refund.

### 6. Action

The refund is processed through the simulated enterprise system.

### 7. Verification

The agent re-reads the resulting enterprise state.

Final state:

```text
Order Status: Refund processed
Resolution:   Refund processed
Verification: SUCCESS
```

---

# 💡 Why This Is Agentic

ResolveX is designed around autonomous execution rather than a one-shot LLM response.

## Goal-driven execution

The agent is given a concrete customer-resolution objective.

## Tool interaction

The agent interacts with multiple simulated enterprise tools.

## Persistent task state

Customer, order, policy, inventory, refund, and replacement state are maintained throughout execution.

## Intermediate observation

Tool results influence subsequent actions.

## Adaptive planning

The agent changes its plan when replacement inventory is unavailable.

## Action execution

The agent performs simulated enterprise actions rather than merely describing what should happen.

## Verification

The final state is independently checked before reporting success.

## Failure recovery

The prototype intentionally contains a scenario where the preferred resolution is blocked by an environmental constraint.

---

# 📊 Example Execution Trace

```text
GOAL
Resolve damaged laptop case
        ↓
OBSERVE
Customer lookup
        ↓
OBSERVE
Order lookup
        ↓
OBSERVE
Policy lookup
        ↓
DECIDE
Replacement is permitted
        ↓
ACT / OBSERVE
Inventory check
        ↓
RESULT
Replacement inventory = 0
        ↓
ADAPT
Original replacement plan is blocked
        ↓
DECIDE
Refund selected as permitted fallback
        ↓
ACT
Process refund
        ↓
VERIFY
Verify resolution
        ↓
FINAL OUTCOME
Resolution verified
```

---

# 🧩 Design Principles

### Investigate before acting

The agent obtains the information required to make a resolution decision.

### Use the environment as feedback

Tool results are treated as observations that can change the plan.

### Do not assume actions succeed

State-changing operations are followed by verification.

### Adapt instead of repeatedly failing

When an intended action is blocked, the agent evaluates alternatives.

### Escalate only when autonomous resolution is not possible

Human intervention is treated as a fallback rather than the default.

---

# 🏆 Hackathon Alignment

ResolveX was developed for:

**Tech Zephyr 4.0 — IIT Bhubaneswar**

**Problem Statement 5 — Smart Automation: Autonomous Customer Resolution Agent**

The prototype focuses on:

- Autonomous customer issue resolution
- Customer and order inspection
- Policy-aware decision making
- Inventory-aware resolution
- Simulated enterprise actions
- Failure recovery
- Adaptive replanning
- Persistent task state
- Final verification

The central demonstration follows:

```text
Goal
  ↓
Decision
  ↓
Action
  ↓
Intermediate Result
  ↓
Adaptation
  ↓
Final Outcome
```

---

# 🔮 Future Improvements

Potential extensions include:

- More enterprise systems and APIs
- Multi-agent customer-support architecture
- More complex policy reasoning
- Partial refunds
- Order cancellation
- Return logistics
- Customer-priority-aware resolution
- SLA monitoring
- Escalation routing
- Audit logs
- Human-in-the-loop approval for high-risk actions
- Persistent database-backed enterprise state
- Evaluation benchmarks across hundreds of simulated cases

---

# 👥 Team

## Vishal B — Team Leader & Lead Developer

Responsible for overall project direction, agent architecture, backend implementation, system integration, and final prototype development.

## Vishal E — AI / Backend Developer

Contributed to the AI agent workflow, backend logic, tool interaction, and simulated enterprise-system integration.

## Saravanan M — Frontend / UI Developer

Contributed to the frontend interface, user experience, agent activity visualization, and demo presentation layer.

---

# 🔗 Project Links

### Live Demo

https://resolvex-qj8k.onrender.com/

### GitHub

https://github.com/b4645857-ai/ResolveX

---

# 📜 License

This project was developed as a hackathon prototype for demonstration and evaluation purposes.

---

## Tech Zephyr 4.0

### ResolveX

**Resolve the case. Don't just answer it.**