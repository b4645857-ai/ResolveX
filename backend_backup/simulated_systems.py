from copy import deepcopy

CUSTOMERS = {
    "CUST-1042": {"id": "CUST-1042", "name": "Aarav Mehta", "tier": "Gold", "email": "aarav@example.test"},
    "CUST-2048": {"id": "CUST-2048", "name": "Maya Rao", "tier": "Standard", "email": "maya@example.test"},
}
ORDERS = {
    "ORD-7712": {"id": "ORD-7712", "customer_id": "CUST-1042", "item": "NovaBook Pro 14", "status": "Delivered", "issue": "Arrived damaged", "price": 1299, "replacement_sku": "NBP14-2026"},
    "ORD-8821": {"id": "ORD-8821", "customer_id": "CUST-2048", "item": "PulseBuds X", "status": "Delivered", "issue": "Wrong color", "price": 149, "replacement_sku": "PBX-BLK"},
}
POLICIES = {
    "damaged": {"replacement": True, "refund": True, "window_days": 30},
    "wrong_color": {"replacement": True, "refund": True, "window_days": 14},
}
INVENTORY = {"NBP14-2026": 0, "PBX-BLK": 12}
STATE = {"orders": deepcopy(ORDERS), "inventory": deepcopy(INVENTORY), "refunds": {}, "replacements": {}}


def reset_state():
    STATE["orders"] = deepcopy(ORDERS)
    STATE["inventory"] = deepcopy(INVENTORY)
    STATE["refunds"] = {}
    STATE["replacements"] = {}


def customer_lookup(customer_id: str):
    return CUSTOMERS.get(customer_id, {"error": "Customer not found"})


def order_lookup(order_id: str):
    return STATE["orders"].get(order_id, {"error": "Order not found"})


def policy_lookup(issue: str):
    key = "wrong_color" if "color" in issue.lower() else "damaged"
    return {"issue_class": key, **POLICIES[key]}


def inventory_check(sku: str):
    return {"sku": sku, "available_units": STATE["inventory"].get(sku, 0), "available": STATE["inventory"].get(sku, 0) > 0}


def create_replacement(order_id: str, sku: str):
    if STATE["inventory"].get(sku, 0) <= 0:
        return {"success": False, "error": "OUT_OF_STOCK", "message": "Replacement inventory is unavailable."}
    STATE["inventory"][sku] -= 1
    STATE["replacements"][order_id] = {"status": "created", "sku": sku}
    STATE["orders"][order_id]["status"] = "Replacement initiated"
    return {"success": True, "replacement_id": f"REP-{len(STATE['replacements'])+300}", "status": "created"}


def process_refund(order_id: str):
    order = STATE["orders"].get(order_id)
    if not order:
        return {"success": False, "error": "ORDER_NOT_FOUND"}
    refund_id = f"REF-{len(STATE['refunds'])+5001}"
    STATE["refunds"][order_id] = {"refund_id": refund_id, "amount": order["price"], "status": "processed"}
    STATE["orders"][order_id]["status"] = "Refund processed"
    return {"success": True, "refund_id": refund_id, "amount": order["price"], "status": "processed"}


def verify_resolution(order_id: str):
    order = STATE["orders"].get(order_id)
    replacement = STATE["replacements"].get(order_id)
    refund = STATE["refunds"].get(order_id)
    resolved = bool(replacement or refund) and order and order["status"] in {"Replacement initiated", "Refund processed"}
    return {"verified": bool(resolved), "order_status": order["status"] if order else None, "replacement": replacement, "refund": refund}

TOOLS = {
    "customer_lookup": customer_lookup,
    "order_lookup": order_lookup,
    "policy_lookup": policy_lookup,
    "inventory_check": inventory_check,
    "create_replacement": create_replacement,
    "process_refund": process_refund,
    "verify_resolution": verify_resolution,
}
