"""
MifugoIQ Backend API
FastAPI server exposing:
  POST /api/chat          — main conversational agent
  POST /api/masumi/report — paid agent service endpoint (Masumi)
  GET  /api/masumi/demo   — demo agent-to-agent flow
  GET  /api/prices        — raw price data for Lovable Price Explorer
  GET  /api/slaughterhouses — directory with Halal filter
  GET  /api/health        — health check
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import agent
import masumi
import neo4j_client as db
import cypher_templates as qt

app = FastAPI(title="MifugoIQ API", version="1.0")

# Allow Lovable frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your Lovable domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#  Request/Response models 

class ChatRequest(BaseModel):
    query: str
    lang: Optional[str] = "auto"  # "en", "sw", or "auto"

class MasumiReportRequest(BaseModel):
    breed: str
    age_class: str
    head: int
    county: str
    payment_ref: Optional[str] = None
    requester_id: Optional[str] = "demo"


#  Endpoints 
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "MifugoIQ"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    """
    Main conversational endpoint — used by Lovable chat UI.
    Accepts natural language in English or Kiswahili.
    Returns grounded, source-cited answer.
    """
    if not req.query or len(req.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        result = agent.query(req.query.strip())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/masumi/report")
def masumi_report(req: MasumiReportRequest):
    """
    Paid agent service endpoint — registered on Masumi network.
    Calling agents send their payment_ref; MifugoIQ verifies then returns the report.
    """
    # Verify payment if a ref was provided (skip in demo/dev mode)
    if req.payment_ref:
        paid = masumi.verify_payment(req.payment_ref, "collateral_valuation")
        if not paid:
            raise HTTPException(status_code=402, detail="Payment not confirmed")

    report = agent.generate_collateral_report(
        req.breed, req.age_class, req.head, req.county
    )
    return report


@app.get("/api/masumi/demo")
def masumi_demo(
    breed: str = "Boran",
    age_class: str = "Store(2-3yr)",
    head: int = 15,
    county: str = "Kajiado",
):
    """
    Full Masumi agent-to-agent demo flow.
    Shows: Lender Agent → payment request → verification → Collateral Report → loan decision.
    """
    result = masumi.demo_lender_agent_flow(breed, age_class, head, county)
    return result


@app.get("/api/prices")
def get_prices(county: Optional[str] = None, breed: Optional[str] = None):
    """
    Price data for the Lovable Price Explorer map/trend chart.
    Optional filters: county, breed.
    """
    cypher, params = qt.all_prices_recent()
    results = db.run_query(cypher, params)

    if county:
        results = [r for r in results if r.get("county", "").lower() == county.lower()]
    if breed:
        results = [r for r in results if breed.lower() in r.get("breed", "").lower()]

    # Serialize dates
    for r in results:
        if "date" in r and hasattr(r["date"], "iso_format"):
            r["date"] = r["date"].iso_format()

    return {"prices": results, "count": len(results)}


@app.get("/api/slaughterhouses")
def get_slaughterhouses(halal_only: bool = False):
    """Directory of slaughterhouses with optional Halal filter."""
    if halal_only:
        cypher, params = qt.halal_slaughterhouses()
    else:
        cypher, params = qt.all_slaughterhouses()
    results = db.run_query(cypher, params)
    return {"slaughterhouses": results, "count": len(results)}


@app.get("/api/feed")
def get_feed_prices(county: str = "Kajiado"):
    """Feed and supplement prices."""
    cypher, params = qt.feed_costs(county)
    results = db.run_query(cypher, params)
    return {"feed_products": results, "count": len(results)}


@app.get("/api/nrv")
def get_nrv(
    breed: str = "Boran",
    age_class: str = "Store(2-3yr)",
    origin_county: str = "Kajiado",
):
    """Net Realizable Value ranking — best market after transport."""
    cypher, params = qt.net_realizable_value(breed, age_class, origin_county)
    results = db.run_query(cypher, params)
    for r in results:
        if "date" in r and hasattr(r["date"], "iso_format"):
            r["date"] = r["date"].iso_format()
    return {"nrv_ranking": results, "origin": origin_county, "breed": breed}


@app.on_event("startup")
def on_startup():
    """Optionally register on Masumi at startup if key is set."""
    if os.environ.get("MASUMI_API_KEY"):
        result = masumi.register_agent()
        print(f"Masumi registration: {result}")


@app.on_event("shutdown")
def on_shutdown():
    db.close()
