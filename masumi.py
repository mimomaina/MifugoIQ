"""
Masumi agent-economy integration for MifugoIQ.
Registers MifugoIQ as a paid agent service and handles incoming payment requests.

Masumi docs: https://docs.masumi.network
"""
import os
import httpx
import json
from typing import Optional

MASUMI_API_KEY = os.environ.get("MASUMI_API_KEY", "")
MASUMI_BASE_URL = os.environ.get("MASUMI_BASE_URL", "https://api.masumi.network/v1")

# Priced service definitions (in USDM / ADA equivalent)
SERVICES = {
    "collateral_valuation": {
        "name": "MifugoIQ Collateral Valuation Report",
        "description": "AI-generated, graph-sourced livestock collateral valuation for AgriFin lenders",
        "price_usdm": 0.50,
        "version": "1.0",
    },
    "finishing_cost": {
        "name": "MifugoIQ Finishing Cost Report",
        "description": "Feed cost estimate for cattle fattening operations by county",
        "price_usdm": 0.25,
        "version": "1.0",
    },
    "nrv_report": {
        "name": "MifugoIQ Net Realizable Value Report",
        "description": "Best-market-net-of-transport ranking for live cattle disposition",
        "price_usdm": 0.25,
        "version": "1.0",
    },
}


def register_agent() -> dict:
    """
    Register MifugoIQ on the Masumi network as a paid agent service.
    Call once during deployment setup.
    """
    if not MASUMI_API_KEY:
        return {"status": "skipped", "reason": "MASUMI_API_KEY not set"}

    headers = {
        "Authorization": f"Bearer {MASUMI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "agent_name": "MifugoIQ Market Intelligence",
        "description": (
            "Knowledge-graph-powered cattle market intelligence for Kenya's beef value chain. "
            "Provides collateral valuation, NRV analysis, and feed cost estimates "
            "sourced from NDMA, KNBS, and DVS data."
        ),
        "services": list(SERVICES.values()),
        "callback_url": os.environ.get("MIFUGOIQ_CALLBACK_URL", ""),
        "supported_payment_tokens": ["USDM", "ADA"],
        "category": "AgriFin",
        "region": "Kenya",
    }
    try:
        resp = httpx.post(
            f"{MASUMI_BASE_URL}/agents/register",
            headers=headers,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def verify_payment(payment_ref: str, service_type: str) -> bool:
    """
    Verify that payment has been received via Masumi for a service request.
    Returns True if payment is confirmed.
    """
    if not MASUMI_API_KEY:
        # Dev mode: skip payment verification
        return os.environ.get("MASUMI_DEV_MODE", "true").lower() == "true"

    headers = {"Authorization": f"Bearer {MASUMI_API_KEY}"}
    try:
        resp = httpx.get(
            f"{MASUMI_BASE_URL}/payments/{payment_ref}/verify",
            headers=headers,
            params={"service": service_type},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("status") == "confirmed"
    except Exception:
        return False


def create_payment_request(service_type: str, requester_id: str) -> dict:
    """
    Create a payment request for a calling agent (e.g. AgriFin Lender Agent).
    Returns payment details the calling agent uses to pay.
    """
    service = SERVICES.get(service_type, SERVICES["collateral_valuation"])

    if not MASUMI_API_KEY:
        # Demo mode: return a mock payment reference
        return {
            "status": "demo_mode",
            "payment_ref": f"DEMO-{service_type.upper()}-001",
            "amount_usdm": service["price_usdm"],
            "service": service["name"],
            "note": "Payment verification skipped in demo mode. Set MASUMI_API_KEY for live payments.",
        }

    headers = {
        "Authorization": f"Bearer {MASUMI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "service_type": service_type,
        "amount_usdm": service["price_usdm"],
        "requester_id": requester_id,
        "memo": f"MifugoIQ {service['name']}",
    }
    try:
        resp = httpx.post(
            f"{MASUMI_BASE_URL}/payments/create",
            headers=headers,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ----- DEMO: AgriFin Lender Agent simulation -----
def demo_lender_agent_flow(breed: str, age_class: str, head: int, county: str) -> dict:
    """
    Simulates the full Masumi agent-to-agent flow for the demo:
    Lender Agent → pays MifugoIQ → receives Collateral Valuation Report.

    This is the exact demo sequence for Section 4.6.2 of the project outline.
    """
    import agent  # local import to avoid circular

    # Step 1: Lender agent requests a payment invoice from MifugoIQ
    payment_req = create_payment_request("collateral_valuation", requester_id="sacco-lender-demo-001")

    # Step 2: Lender agent pays (simulated)
    payment_ref = payment_req.get("payment_ref", "DEMO-001")

    # Step 3: MifugoIQ verifies payment
    paid = verify_payment(payment_ref, "collateral_valuation")

    if not paid:
        return {"status": "payment_failed", "payment_ref": payment_ref}

    # Step 4: MifugoIQ generates the Collateral Valuation Report
    report = agent.generate_collateral_report(breed, age_class, head, county)

    # Step 5: Lender agent computes loan-to-value decision
    nrv = report.get("net_realizable_value_kes", 0)
    ltv_pct = report.get("suggested_ltv_pct", 65)
    loan_limit = int(nrv * ltv_pct / 100)

    return {
        "flow": "agent_to_agent_masumi_demo",
        "step_1_payment_request": payment_req,
        "step_2_payment_ref": payment_ref,
        "step_3_payment_verified": paid,
        "step_4_collateral_report": report,
        "step_5_lender_decision": {
            "net_realizable_value_kes": nrv,
            "ltv_pct": ltv_pct,
            "recommended_loan_limit_kes": loan_limit,
            "decision": "APPROVE" if loan_limit > 0 else "DECLINE",
            "decision_note": (
                f"Based on NRV of KES {nrv:,}, "
                f"applying {ltv_pct}% LTV = loan limit KES {loan_limit:,}. "
                f"Risk flag: {report.get('underwriting_recommendation', 'N/A')}"
            ),
        },
    }
