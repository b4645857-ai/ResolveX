import json
import os
from typing import Any
from dotenv import load_dotenv
from .simulated_systems import TOOLS

load_dotenv()

SYSTEM_PROMPT = """You are ResolveX, an autonomous customer-resolution agent operating ONLY inside a simulated enterprise environment.
Your goal is to resolve the customer's issue, not merely draft a reply.
You have tools for customer, order, policy, inventory, replacement, refund, and verification.
Choose the next action based on current state and tool results. If an action fails or a constraint changes, replan.
Never invent tool results. Always verify the final state before declaring success.
For a damaged-item replacement scenario, a replacement may be unavailable; in that case inspect policy and use an eligible refund as a fallback.
Return one JSON object only with keys: action, args, rationale, done.
Allowed actions: customer_lookup, order_lookup, policy_lookup, inventory_check, create_replacement, process_refund, verify_resolution.
"""


def call_llm(state: dict, history: list[dict]) -> dict | None:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        prompt = {"state": state, "history": history}
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            instructions=SYSTEM_PROMPT,
            input=json.dumps(prompt),
        )
        text = response.output_text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return None


def deterministic_plan(state: dict) -> dict:
    # Fallback is intentionally state-aware: it still observes results, selects tools, adapts on failure, and verifies.
    if not state.get("customer"): return {"action": "customer_lookup", "args": {"customer_id": state["customer_id"]}, "rationale": "Identify the customer and establish case ownership.", "done": False}
    if not state.get("order"): return {"action": "order_lookup", "args": {"order_id": state["order_id"]}, "rationale": "Inspect the current order and issue context.", "done": False}
    if not state.get("policy"): return {"action": "policy_lookup", "args": {"issue": state["order"].get("issue", state["issue"])}, "rationale": "Check which resolutions are permitted for this case.", "done": False}
    if not state.get("inventory_checked") and not state.get("adapted"):
        return {"action": "inventory_check", "args": {"sku": state["order"]["replacement_sku"]}, "rationale": "Check whether the requested replacement is feasible before taking a state-changing action.", "done": False}
    if state.get("inventory_available") and not state.get("replacement"):
        return {"action": "create_replacement", "args": {"order_id": state["order_id"], "sku": state["order"]["replacement_sku"]}, "rationale": "Replacement is available and permitted; execute the requested resolution.", "done": False}
    if not state.get("inventory_available") and not state.get("refund"):
        return {"action": "process_refund", "args": {"order_id": state["order_id"]}, "rationale": "Replacement is blocked by inventory, so adapt to the eligible refund path.", "done": False}
    return {"action": "verify_resolution", "args": {"order_id": state["order_id"]}, "rationale": "Verify the state-changing action produced the intended outcome.", "done": False}


def run_case(customer_id: str, order_id: str, issue: str, scenario: str = "auto") -> dict:
    from .simulated_systems import reset_state
    reset_state()
    state: dict[str, Any] = {"customer_id": customer_id, "order_id": order_id, "issue": issue, "customer": None, "order": None, "policy": None, "inventory_checked": False, "inventory_available": None, "replacement": None, "refund": None, "adapted": False, "verified": False}
    trace = []
    history = []
    for step in range(1, 10):
        plan = call_llm(state, history) or deterministic_plan(state)
        action = plan["action"]
        args = plan.get("args", {})
        before = {k: state.get(k) for k in ["adapted", "inventory_available", "replacement", "refund", "verified"]}
        try:
            result = TOOLS[action](**args)
        except Exception as exc:
            result = {"success": False, "error": str(exc)}
        if action == "customer_lookup": state["customer"] = result
        elif action == "order_lookup": state["order"] = result
        elif action == "policy_lookup": state["policy"] = result
        elif action == "inventory_check":
            state["inventory_checked"] = True; state["inventory_available"] = result.get("available", False)
            if not state["inventory_available"]:
                state["adapted"] = True
        elif action == "create_replacement": state["replacement"] = result if result.get("success") else None
        elif action == "process_refund": state["refund"] = result if result.get("success") else None
        elif action == "verify_resolution": state["verified"] = result.get("verified", False)
        event = {"step": step, "action": action, "args": args, "rationale": plan.get("rationale", ""), "result": result, "status": "success" if not result.get("error") and result.get("success", True) else "blocked"}
        if action == "inventory_check" and not result.get("available"):
            event["status"] = "blocked"; event["adaptation"] = "Replacement unavailable → switching to refund path."
        if state.get("adapted") and before.get("adapted") is False and action == "inventory_check":
            event["adaptation"] = "Constraint detected; replanning around inventory availability."
        trace.append(event)
        history.append(event)
        if state["verified"]:
            break
    return {"success": state["verified"], "state": state, "trace": trace, "summary": build_summary(state, trace)}


def build_summary(state, trace):
    if state.get("replacement"):
        return f"Replacement created for {state['order_id']} and verified successfully."
    if state.get("refund"):
        return f"Replacement was unavailable, so ResolveX adapted to a refund of ₹{state['refund']['amount']} and verified the resolution."
    return "Case could not be verified as resolved."
