"""
MifugoIQ GraphRAG Agent
Flow: query → intent detection → Cypher → Neo4j → LLM answer composition
LLM served via Featherless (OpenAI-compatible endpoint).
"""
import os
import re
import json
import httpx
from typing import Optional
import neo4j_client as db
import cypher_templates as qt

FEATHERLESS_API_KEY = os.environ["FEATHERLESS_API_KEY"]
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"

MODEL = os.environ.get("FEATHERLESS_MODEL", "Qwen/Qwen2.5-7B-Instruct")

SYSTEM_PROMPT = """You are MifugoIQ, a market intelligence assistant for Kenya's cattle and beef value chain.
You help breeders, finishers, traders, and financial institutions make decisions using grounded, sourced data.

RULES (non-negotiable):
1. Never state a price, fee, or figure not present in the graph data provided to you.
2. If data is unavailable, say so explicitly — do not invent numbers.
3. When stating a figure, always cite its source and date (e.g. "per NDMA May 2026 bulletin").
4. Respond in the same language the user wrote in (English or Kiswahili/Sheng).
5. Be concise and practical — users are making real financial decisions.
6. For collateral valuation reports, always include: per-head price, head count, total gross value, transport deduction, net realizable value, and an underwriting risk flag.

TONE: Professional, helpful, grounded. You are a trusted data layer, not a chatbot."""


def _featherless_chat(messages: list[dict], max_tokens: int = 800) -> str:
    """Call Featherless OpenAI-compatible chat endpoint."""
    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.1,  # Low temp for factual answers
    }
    resp = httpx.post(
        f"{FEATHERLESS_BASE_URL}/chat/completions",
        headers=headers,
        json=payload, 
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _detect_intent(query: str) -> dict:
    """
    Classify query intent and extract entities.
    Returns: {intent, breed, age_class, county, county_b, head, days}
    """
    q = query.lower()

    # Entity extraction patterns
    breeds = {
        "boran": "Boran", "zebu": "Zebu", "sahiwal": "Sahiwal-cross",
        "friesian": "Friesian", "ayrshire": "Ayrshire",
        "ng'ombe wa boran": "Boran", "ng'ombe": "Zebu",
    }
    age_classes = {
        "store": "Store(2-3yr)", "2-3": "Store(2-3yr)", "2yr": "Store(2-3yr)",
        "mature": "Mature(3+yr)", "3+": "Mature(3+yr)", "finished": "Mature(3+yr)",
        "weaner": "Weaner(1-2yr)", "yearling": "Weaner(1-2yr)", "1-2": "Weaner(1-2yr)",
        "miaka 2": "Store(2-3yr)", "miaka 3": "Mature(3+yr)",
    }
    counties = [
        "kajiado", "nairobi", "machakos", "nakuru", "garissa",
        "isiolo", "narok", "mombasa", "kitui", "marsabit",
    ]

    breed = next((v for k, v in breeds.items() if k in q), "Boran")
    age_class = next((v for k, v in age_classes.items() if k in q), "Store(2-3yr)")
    found_counties = [c.title() for c in counties if c in q]
    county = found_counties[0] if found_counties else "Kajiado"
    county_b = found_counties[1] if len(found_counties) > 1 else None

    # Head count extraction
    head_match = re.search(r"(\d+)\s*(steers?|bulls?|cattle|head|ng'ombe)", q)
    head = int(head_match.group(1)) if head_match else 1

    # Days extraction
    days_match = re.search(r"(\d+)\s*days?", q)
    days = int(days_match.group(1)) if days_match else 90

    # Intent classification
    if any(w in q for w in ["collateral", "loan", "value my", "thamani ya", "lend", "underwrite", "ltv"]):
        intent = "collateral_valuation"
    elif any(w in q for w in ["best market", "where sell", "where should i sell", "wapi niuze", "net price", "nrv"]):
        intent = "net_realizable_value"
    elif any(w in q for w in ["compare", "vs", "versus", "linganisha", "between"]) and county_b:
        intent = "price_comparison"
    elif any(w in q for w in ["halal", "slaughter", "abattoir", "machinjio"]):
        intent = "halal_slaughterhouse"
    elif any(w in q for w in ["feed", "chakula", "dairy meal", "mineral", "supplement", "finishing cost", "ration"]):
        intent = "feed_cost"
    elif any(w in q for w in ["risk", "drought", "water trek", "vci", "friction", "weather"]):
        intent = "friction_metrics"
    elif any(w in q for w in ["price", "bei", "cost", "how much", "ngapi", "what is"]):
        intent = "price_lookup"
    else:
        intent = "price_lookup"  # safe default

    return {
        "intent": intent, "breed": breed, "age_class": age_class,
        "county": county, "county_b": county_b, "head": head, "days": days,
    }


def _run_graph_query(entities: dict) -> tuple[list[dict], str]:
    """Select and run the appropriate Cypher template. Returns (results, query_description)."""
    intent = entities["intent"]
    try:
        if intent == "collateral_valuation":
            cypher, params = qt.collateral_valuation(
                entities["breed"], entities["age_class"], entities["head"], entities["county"]
            )
            desc = f"Collateral valuation for {entities['head']} {entities['breed']} {entities['age_class']} in {entities['county']}"
        elif intent == "net_realizable_value":
            cypher, params = qt.net_realizable_value(
                entities["breed"], entities["age_class"], entities["county"]
            )
            desc = f"NRV ranking from {entities['county']} for {entities['breed']} {entities['age_class']}"
        elif intent == "price_comparison":
            cypher, params = qt.price_comparison(
                entities["breed"], entities["age_class"], entities["county"], entities["county_b"]
            )
            desc = f"Price comparison: {entities['county']} vs {entities['county_b']}"
        elif intent == "halal_slaughterhouse":
            cypher, params = qt.halal_slaughterhouses(entities["county"])
            desc = "Halal-certified slaughterhouses directory"
        elif intent == "feed_cost":
            cypher, params = qt.feed_costs(entities["county"])
            desc = f"Feed product prices near {entities['county']}"
        elif intent == "friction_metrics":
            cypher, params = qt.friction_metrics(entities["county"])
            desc = f"Environmental risk metrics for {entities['county']}"
        else:  # price_lookup
            cypher, params = qt.price_lookup(
                entities["breed"], entities["age_class"], entities["county"]
            )
            desc = f"Price lookup: {entities['breed']} {entities['age_class']} in {entities['county']}"

        results = db.run_query(cypher, params)
        return results, desc
    except Exception as e:
        return [], f"Query error: {e}"


def _compose_answer(query: str, entities: dict, graph_data: list[dict], query_desc: str) -> str:
    """Use Featherless LLM to compose a grounded, cited natural-language answer."""
    if not graph_data:
        # No data found — honest response
        return (
            f"Samahani / I'm sorry — no data is currently available in the MifugoIQ graph for "
            f"'{query_desc}'. This may mean the data has not yet been ingested for that "
            f"county/breed combination. Please check back as new NDMA bulletins are loaded."
        )

    graph_json = json.dumps(graph_data, indent=2, default=str)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"User query: {query}\n\n"
                f"Query context: {query_desc}\n\n"
                f"Graph data retrieved:\n{graph_json}\n\n"
                f"Compose a clear, sourced answer to the user's query using ONLY the data above. "
                f"Always cite the source and date. For financial figures, show the calculation."
            ),
        },
    ]
    return _featherless_chat(messages)


def query(user_query: str) -> dict:
    """
    Main entry point. Returns:
    {answer, intent, entities, graph_data, model}
    """
    entities = _detect_intent(user_query)
    graph_data, query_desc = _run_graph_query(entities)
    answer = _compose_answer(user_query, entities, graph_data, query_desc)

    return {
        "answer": answer,
        "intent": entities["intent"],
        "entities": entities,
        "graph_data": graph_data,
        "model": MODEL,
        "query_description": query_desc,
    }


def generate_collateral_report(breed: str, age_class: str, head: int, county: str) -> dict:
    """
    Structured collateral valuation report — used by Masumi agent service.
    Returns JSON-serializable dict suitable for AgriFin lender consumption.
    """
    cypher, params = qt.collateral_valuation(breed, age_class, head, county)
    results = db.run_query(cypher, params)

    if not results:
        return {
            "status": "no_data",
            "message": f"No price data for {breed} {age_class} in {county}",
        }

    r = results[0]
    report = {
        "report_type": "Collateral Valuation Report",
        "generated_by": "MifugoIQ GraphRAG Engine",
        "data_source": r.get("source", "NDMA"),
        "price_date": str(r.get("priceDate", "")),
        "breed": r.get("breed", breed),
        "age_class": r.get("ageClass", age_class),
        "county": county,
        "reference_market": r.get("market", ""),
        "per_head_price_kes": r.get("perHeadKES", 0),
        "head_count": head,
        "total_gross_kes": r.get("totalGrossKES", 0),
        "transport_cost_per_head_kes": r.get("transportCostPerHead", 0),
        "net_realizable_value_kes": r.get("netRealizableValueKES", 0),
        "environmental_water_trek_km": r.get("waterTrekKm"),
        "underwriting_recommendation": r.get("underwritingFlag", "Insufficient data"),
        "suggested_ltv_pct": _ltv_from_flag(r.get("underwritingFlag", "")),
        "disclaimer": (
            "This report is a decision-support tool. Final lending decisions "
            "require human sign-off. Prices sourced from NDMA/KNBS bulletins "
            "and may be up to 30 days old."
        ),
    }
    return report


def _ltv_from_flag(flag: str) -> int:
    if "High Risk" in flag:
        return 50
    if "Moderate Risk" in flag:
        return 65
    return 75
