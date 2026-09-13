from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .agent import run_case

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="ResolveX")
app.mount("/assets", StaticFiles(directory=ROOT / "frontend"), name="assets")

class Case(BaseModel):
    customer_id: str = "CUST-1042"
    order_id: str = "ORD-7712"
    issue: str = "My laptop arrived damaged. I want a replacement."
    scenario: str = "auto"

@app.get("/")
def index():
    return FileResponse(ROOT / "frontend" / "index.html")

@app.get("/api/cases")
def cases():
    return {"cases": [
        {"id":"damaged-out-of-stock","label":"Damaged laptop · replacement unavailable","customer_id":"CUST-1042","order_id":"ORD-7712","issue":"My laptop arrived damaged. I want a replacement."},
        {"id":"wrong-color","label":"Wrong color · replacement available","customer_id":"CUST-2048","order_id":"ORD-8821","issue":"I received the wrong color. I want the correct one."},
    ]}

@app.post("/api/resolve")
def resolve(case: Case):
    return run_case(case.customer_id, case.order_id, case.issue, case.scenario)
