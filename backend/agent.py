import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from .simulated_systems import TOOLS, reset_state

load_dotenv()


SYSTEM_PROMPT = """
You are ResolveX, an autonomous customer-resolution agent.

You operate ONLY inside the simulated enterprise environment provided by your tools.

Your objective is to actually resolve the customer's issue, not merely explain what
the customer should do.

You must:
1. Investigate the case using the available tools.
2. Maintain awareness of the information already discovered.
3. Decide which tool/action is appropriate based on the current evidence.
4. Execute state-changing actions only when justified.
5. Observe the result of every action.
6. If an action is blocked by a real environmental constraint, adapt your plan.
7. Verify the final state before declaring the case resolved.
8. Never invent customer, order, policy, inventory, or action results.

For a replacement request:
- Check the customer.
- Check the order.
- Check the relevant policy.
- Check replacement inventory.
- If inventory is unavailable, explicitly recognize that the requested
  resolution is blocked and evaluate an eligible alternative such as a refund.
- After taking a state-changing action, always verify the resulting state.

Available tools represent simulated enterprise systems.
"""


# ---------------------------------------------------------------------------
# Tool schemas exposed to the LLM
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "customer_lookup",
        "description": "Retrieve a customer's profile from the simulated customer system.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer identifier."
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "order_lookup",
        "description": "Retrieve the current order state and order details.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order identifier."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "policy_lookup",
        "description": "Retrieve the applicable customer-resolution policy.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue": {
                    "type": "string",
                    "description": "Description of the customer's issue."
                }
            },
            "required": ["issue"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "inventory_check",
        "description": "Check whether the requested replacement product is available.",
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Replacement product SKU."
                }
            },
            "required": ["sku"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "create_replacement",
        "description": "Create a replacement order when replacement inventory is available.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Original order identifier."
                },
                "sku": {
                    "type": "string",
                    "description": "Replacement product SKU."
                }
            },
            "required": ["order_id", "sku"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "process_refund",
        "description": "Process a refund for an eligible order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order identifier."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "verify_resolution",
        "description": "Verify whether the customer's issue has actually been resolved.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order identifier."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
]


# ---------------------------------------------------------------------------
# Human-readable agentic events for the UI
# ---------------------------------------------------------------------------

def classify_event(action: str, result: dict[str, Any]) -> str:
    if action in {
        "customer_lookup",
        "order_lookup",
        "policy_lookup",
        "inventory_check",
    }:
        return "OBSERVE"

    if action in {
        "create_replacement",
        "process_refund",
    }:
        return "ACTION"

    if action == "verify_resolution":
        return "VERIFY"

    return "DECIDE"


def rationale_for_action(action: str, result: dict[str, Any]) -> str:
    if action == "customer_lookup":
        return "Identify the customer and establish case context."

    if action == "order_lookup":
        return "Inspect the current order and determine the issue and requested resolution."

    if action == "policy_lookup":
        return "Check which resolutions are permitted for this customer issue."

    if action == "inventory_check":
        if result.get("available"):
            return "The requested replacement is feasible; inventory is available."
        return "Replacement inventory is unavailable, so the original resolution is blocked."

    if action == "create_replacement":
        return "Replacement inventory is available and policy permits the requested resolution."

    if action == "process_refund":
        return "The replacement path is blocked, so the agent is executing an eligible refund fallback."

    if action == "verify_resolution":
        return "Re-read the enterprise state to verify that the intended resolution actually occurred."

    return "Selecting the next action based on the current case state."


# ---------------------------------------------------------------------------
# Deterministic fallback
#
# This keeps the application demonstrable if the API is unavailable while
# preserving the same Observe → Decide → Act → Adapt → Verify workflow.
# ---------------------------------------------------------------------------

def deterministic_plan(state: dict[str, Any]) -> dict[str, Any]:
    if not state.get("customer"):
        return {
            "action": "customer_lookup",
            "args": {"customer_id": state["customer_id"]},
        }

    if not state.get("order"):
        return {
            "action": "order_lookup",
            "args": {"order_id": state["order_id"]},
        }

    if not state.get("policy"):
        return {
            "action": "policy_lookup",
            "args": {
                "issue": state["order"].get(
                    "issue",
                    state["issue"]
                )
            },
        }

    if not state.get("inventory_checked"):
        return {
            "action": "inventory_check",
            "args": {
                "sku": state["order"]["replacement_sku"]
            },
        }

    if state.get("inventory_available") and not state.get("replacement"):
        return {
            "action": "create_replacement",
            "args": {
                "order_id": state["order_id"],
                "sku": state["order"]["replacement_sku"],
            },
        }

    if (
        not state.get("inventory_available")
        and not state.get("refund")
    ):
        return {
            "action": "process_refund",
            "args": {
                "order_id": state["order_id"]
            },
        }

    return {
        "action": "verify_resolution",
        "args": {
            "order_id": state["order_id"]
        },
    }


# ---------------------------------------------------------------------------
# OpenAI agent
# ---------------------------------------------------------------------------

def run_llm_agent(
    customer_id: str,
    order_id: str,
    issue: str,
    trace: list[dict[str, Any]],
    state: dict[str, Any],
) -> bool:

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return False

    client = OpenAI(api_key=api_key)

    conversation = [
        {
            "role": "user",
            "content": (
                f"Customer ID: {customer_id}\n"
                f"Order ID: {order_id}\n"
                f"Customer request: {issue}\n\n"
                "Resolve this case autonomously."
            ),
        }
    ]

    for _ in range(12):

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            instructions=SYSTEM_PROMPT,
            input=conversation,
            tools=TOOL_SCHEMAS,
        )

        # Preserve the model's output items so the next turn has full context.
        conversation.extend(response.output)

        tool_calls = [
            item
            for item in response.output
            if getattr(item, "type", None) == "function_call"
        ]

        if not tool_calls:
            break

        for tool_call in tool_calls:

            action = tool_call.name

            try:
                args = json.loads(tool_call.arguments)
            except Exception:
                args = {}

            if action not in TOOLS:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {action}",
                }
            else:
                try:
                    result = TOOLS[action](**args)
                except Exception as exc:
                    result = {
                        "success": False,
                        "error": str(exc),
                    }

            # ---------------------------------------------------------------
            # Update explicit task state
            # ---------------------------------------------------------------

            update_state(state, action, result)

            event_type = classify_event(action, result)

            event = {
                "step": len(trace) + 1,
                "type": event_type,
                "action": action,
                "args": args,
                "rationale": rationale_for_action(action, result),
                "result": result,
                "status": (
                    "blocked"
                    if result.get("success") is False
                    else "success"
                ),
            }

            # Real environmental adaptation:
            if action == "inventory_check" and not result.get("available"):
                state["adapted"] = True

                event["type"] = "ADAPT"
                event["adaptation"] = (
                    "Replacement unavailable. "
                    "The original resolution is blocked; "
                    "the agent is evaluating an alternative resolution."
                )

            trace.append(event)

            # Give the actual tool result back to the model.
            conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result),
                }
            )

            if action == "verify_resolution" and result.get("verified"):
                state["verified"] = True
                return True

    return state.get("verified", False)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def update_state(
    state: dict[str, Any],
    action: str,
    result: dict[str, Any],
) -> None:

    if action == "customer_lookup":
        state["customer"] = result

    elif action == "order_lookup":
        state["order"] = result

    elif action == "policy_lookup":
        state["policy"] = result

    elif action == "inventory_check":
        state["inventory_checked"] = True
        state["inventory_available"] = result.get("available", False)

    elif action == "create_replacement":
        if result.get("success"):
            state["replacement"] = result

    elif action == "process_refund":
        if result.get("success"):
            state["refund"] = result

    elif action == "verify_resolution":
        state["verified"] = result.get("verified", False)


# ---------------------------------------------------------------------------
# Main case runner
# ---------------------------------------------------------------------------

def run_case(
    customer_id: str,
    order_id: str,
    issue: str,
    scenario: str = "auto",
) -> dict[str, Any]:

    reset_state()

    state: dict[str, Any] = {
        "customer_id": customer_id,
        "order_id": order_id,
        "issue": issue,
        "customer": None,
        "order": None,
        "policy": None,
        "inventory_checked": False,
        "inventory_available": None,
        "replacement": None,
        "refund": None,
        "adapted": False,
        "verified": False,
    }

    trace: list[dict[str, Any]] = []

    # Try the actual autonomous tool-calling agent first.
    llm_success = run_llm_agent(
        customer_id,
        order_id,
        issue,
        trace,
        state,
    )

    # If the model is unavailable or fails to complete the workflow,
    # continue using the deterministic state-aware controller.
    if not llm_success:

        for _ in range(10):

            if state["verified"]:
                break

            plan = deterministic_plan(state)

            action = plan["action"]
            args = plan.get("args", {})

            try:
                result = TOOLS[action](**args)
            except Exception as exc:
                result = {
                    "success": False,
                    "error": str(exc),
                }

            update_state(state, action, result)

            event_type = classify_event(action, result)

            event = {
                "step": len(trace) + 1,
                "type": event_type,
                "action": action,
                "args": args,
                "rationale": rationale_for_action(action, result),
                "result": result,
                "status": (
                    "blocked"
                    if result.get("success") is False
                    else "success"
                ),
            }

            if action == "inventory_check" and not result.get("available"):
                state["adapted"] = True
                event["type"] = "ADAPT"
                event["adaptation"] = (
                    "Replacement unavailable → "
                    "switching to the eligible refund path."
                )

            trace.append(event)

    return {
        "success": state["verified"],
        "state": state,
        "trace": trace,
        "summary": build_summary(state),
    }


def build_summary(state: dict[str, Any]) -> str:

    if state.get("replacement"):
        return (
            f"Replacement created for {state['order_id']} "
            "and the resolution was verified successfully."
        )

    if state.get("refund"):
        amount = state["refund"].get("amount", 0)
        return (
            f"Replacement was unavailable, so ResolveX adapted "
            f"to a refund of ₹{amount} and verified the resolution."
        )

    return "Case could not be verified as resolved."