## **MifugoIQ 🐄** 

## **Kenya's Cattle Value Chain — Knowledge-Graph Intelligence Engine** 

**Kenya AI Challenge 2026 · AgriFin Track · Mercy Corps AgriFin Network** Built for the Neo4j · F
## **1. The Problem** 

Kenya's cattle economy is worth hundreds of billions of shillings annually and forms the primary livelihood for an estimated **6.36 million smallholder and pastoralist households** . The national herd stands at roughly 18 million cattle — yet at almost every handoff in the value chain, critical market information is lost, siloed, or inaccessible. 

The AgriFin gap is specific: **livestock pledged as loan collateral grew 53.6% year-onyear to June 2025** (Business Registration Services data), meaning lenders already want to lend against cattle. But appetite has outrun infrastructure. A SACCO loan officer in Kajiado evaluating a KSh 500,000 loan secured by 15 Boran steers has no defensible way to answer: 

_"What are these steers actually worth today, and what would I realistically recover if I had to call the loan?"_ 

The data to answer that question already exists — scattered across NDMA monthly bulletins, KNBS Statistical Abstracts, KMC reference prices, and DVS abattoir registers — but it is published as **static PDFs, on monthly cycles, siloed by institution** , and entirely unqueryable by a loan officer in a three-minute credit committee meeting. 

MifugoIQ is the connective tissue that fixes this. 

## **2. What MifugoIQ Does** 

MifugoIQ is a **knowledge-graph-powered AI agent** that maps the entire Kenyan cattle value chain into a single, continuously-updated, queryable intelligence layer. Anyone in the chain can ask a natural-language question in **English, Kiswahili, or Sheng** and get a grounded, sourced, location- and breed-specific answer. 


## 3. System Architecture & Technology Integration
MifugoIQ integrates the four core sponsor technologies into a cohesive, production-grade pipeline. Each technology serves a distinct, load-bearing function in the architecture.

| Layer | Technology | Function in MifugoIQ |
| :--- | :--- | :--- |
| **Knowledge Layer** | **Neo4j** | Stores the entire value chain (breeders, markets, feedlots, slaughterhouses, transporters) as a connected graph with time-stamped price observations. Powers GraphRAG traversals. |
| **Reasoning Layer** | **Featherless** | Hosts the open-source LLMs (e.g., Qwen2.5) that power the conversational agent. Handles multilingual (English/Kiswahili) query understanding, Text-to-Cypher translation, and grounded report generation. |
| **Application Layer** | **Lovable** | Builds the entire user-facing web application: chat interface, price dashboards, county price heatmaps, value-chain explorer, and finishing cost calculators. |
| **Agent Economy** | **Masumi** | Registers MifugoIQ as a paid agent service. Enables external AI agents (e.g., an AgriFin lender's underwriting bot) to pay per query in ADA/USDM for verified collateral valuation reports. |

---
## 4. Knowledge Graph Architecture (Neo4j)
The current repository represents the completion of the Data Ingestion and Ontology Mapping milestone. We have successfully extracted, normalized, and loaded Tier 1 and Tier 2 institutional datasets into a production-grade Neo4j graph schema.

### 4.1 Ingested Data Sources
*   **NDMA Early Warning Bulletins (Kajiado County - Feb, Apr, May 2026):** Extracted time-series price observations for cattle and goats across specific livelihood zones (Pastoral, Agro-Pastoral, Mixed Farming), alongside critical biophysical friction metrics (Vegetation Condition Index, livestock water trekking distances, and body condition scores).
*   **DVS Export Slaughterhouse Registry:** Ingested the official directory of government-approved export abattoirs (e.g., Kenya Meat Commission, Farmers Choice, Quality Meat Packers), including location data, capacity indicators, and Halal certification status.
*   **Feed & Logistics Benchmarks:** Seeded baseline nodes for feed products (e.g., dairy meal, mineral licks) and regional transport cost benchmarks to enable Net Realizable Value (NRV) calculations.

### 4.2 Knowledge Graph Ontology
The graph is structured to support complex, multi-hop GraphRAG traversals required for financial underwriting and supply chain optimization.

#### Core Node Labels & Properties
| Node Label | Represents | Key Properties |
| :--- | :--- | :--- |
| **`County`** | Administrative geography | `name`, `region` |
| **`Market`** | Primary auction / trading point | `name`, `marketType`, `livelihoodZone` |
| **`Breed`** | Cattle genetics | `name`, `originType` (Indigenous/Improved) |
| **`AnimalClass`** | Demographic cohort | `ageClass`, `sex`, `bodyConditionScore` |
| **`PriceObservation`** | Time-stamped financial data | `priceKES`, `date`, `source`, `minKES`, `maxKES` |
| **`Slaughterhouse`** | Processing facility | `name`, `capacityHeadPerDay`, `halalCertified`, `slaughterFeeKES` |
| **`Transporter`** | Logistics provider | `vehicleType`, `costBenchmarkKES` |
| **`FrictionMetric`** | Biophysical / Environmental risk | `type` (e.g., Water Trek), `value`, `unit`, `date` |

### Core Relationship Types (Edges)
| Relationship Pattern | Business Logic & Traversal Purpose |
| :--- | :--- |
| `(Market)-[:LOCATED_IN]->(County)` | Anchors price discovery to specific geographic and infrastructural zones. |
| `(AnimalClass)-[:OF_BREED]->(Breed)` | Links demographic cohorts to genetic lineages for breed-premium analysis. |
| `(AnimalClass)-[:PRICED_AT]->(PriceObservation)-[:RECORDED_AT]->(Market)` | Establishes the time-series financial valuation of specific asset classes. |
| `(Transporter)-[:SERVICES]->(County)` | Defines logistics coverage to calculate transport deductions for NRV. |
| `(County)-[:HAS_METRIC]->(FrictionMetric)` | Attaches environmental risk data (e.g., drought stress) to origin locations for risk-adjusted collateral valuation. |

### 4.3 Expected Graph Outputs & Flagship Queries
The architecture is specifically optimized for multi-hop GraphRAG reasoning. Below are the core Cypher query patterns that power the MifugoIQ intelligence layer.

#### Visualise graph connections
```cypher
CALL db.schema.visualization()
```

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50
```


```cypher
// Calculate the best net price for Boran Steers originating in Kajiado, factoring in transport costs to terminal markets
MATCH (cohort:AnimalClass {ageClass: 'Store(2-3yr)', sex: 'Male'})-[:OF_BREED]->(:Breed {name: 'Boran'})
MATCH (cohort)-[:PRICED_AT]->(obs:PriceObservation)-[:RECORDED_AT]->(market:Market)-[:LOCATED_IN]->(destCounty:County)
MATCH (transporter:Transporter)-[:SERVICES]->(origin:County {name: 'Kajiado'})
MATCH (transporter)-[:SERVICES]->(destCounty)
WHERE obs.date >= date('2026-04-01')
RETURN 
    market.name AS targetMarket, 
    obs.priceKES AS grossPrice, 
    transporter.costBenchmarkKES AS transportCost, 
    (obs.priceKES - transporter.costBenchmarkKES) AS netRealizableValue 
ORDER BY netRealizableValue DESC 
LIMIT 3;
```

```cypher
// Evaluate origin county friction metrics to adjust collateral risk profiles
MATCH (c:County {name: 'Kajiado'})-[:HAS_METRIC]->(f:FrictionMetric {type: 'Livestock Water Trek'})
WHERE f.date >= date('2026-02-01')
RETURN 
    c.name AS county, 
    f.value AS waterTrekKm, 
    CASE 
        WHEN f.value > 4.5 THEN 'High Risk: Reduce LTV (Herd Caloric Stress)'
        WHEN f.value > 3.0 THEN 'Moderate Risk: Standard LTV'
        ELSE 'Low Risk: Premium LTV'
    END AS underwritingRecommendation;
```
## **7. GraphRAG Agent — Featherless** 

## **7.1 Pipeline** 

The agent in backend/agent.py follows a strict, grounded pipeline: 

User query (EN / SW) │ ▼ Intent detection           — keyword + pattern matching Entity extraction          — breed, age class, county, head count, days │ 

▼ Cypher template selection  — cypher_templates.py (7 intent categories: price_lookup · net_realizable_value · price_comparison · halal_slaughterhouse · feed_cost · collateral_valuation · friction_metrics) │ ▼ 

Neo4j query execution      — neo4j_client.py → AuraDB │ ▼ 

Grounding check            — if results empty → honest "no data" response │ ▼ 

Featherless LLM call       — compose cited answer in user's language │ ▼ 

Response                   — grounded answer with source + date citations 

## **7.2 Model** 

**Primary:** Qwen/Qwen2.5-7B-Instruct via Featherless OpenAI-compatible endpoint 

- Strong instruction-following for structured reasoning tasks 

- Reliable English + Kiswahili output 

- Fast enough for live demo latency 

**Fallback:** Qwen/Qwen2.5-14B-Instruct (upgrade via FEATHERLESS_MODEL env var if quality needs improvement) 

## **7.3 Grounding Rules (Non-Negotiable)** 

The agent system prompt enforces three hard constraints: 

1. **Never fabricate a number.** Every price, fee, or cost must come from a graph query result. If the graph returns no data, the agent says so explicitly. 

2. **Always cite the source.** Every figure is tagged with its data source (e.g. "per NDMA May 2026 bulletin") and date. 

3. **Respond in the user's language.** English in → English out. Kiswahili in → Kiswahili out. Sheng → Kiswahili/English mix. 

## **7.4 Sample Interactions** 

**User Input Languag What Happens e** 

|"Ni bei gani ya ng'ombe wa|Kiswahili|Price lookup<br>Cypher<br>NDMA price data<br>→<br>→|
|---|---|---|
|Boran miaka 2–3 huko<br>Kajiado?"||Kiswahili response with source<br>→|
|"Value 15 Boran steers, 2–3|English|Collateral valuation<br>multi-hop Cypher<br>→|
|years, Kajiado, as loan<br>collateral"||(price + transport + friction)<br>structured<br>→<br>report with LTV fag|
|"Best market for my 15|English|NRV query<br>ranks markets by (price<br>→<br>−|
|steers from Kajiado this<br>week, all-in?"||transport cost)<br>recommended market<br>→<br>with net fgure|
|"Which Halal abattoirs can I|English|Halal flter query<br>facility list with<br>→|
|use near Garissa?"||capacity and fees|



## **8. Backend API** 

The FastAPI server (backend/main.py) exposes 7 endpoints consumed by both the Lovable frontend and the Masumi agent network. 

## **Endpoints** 

|**Method**|**Path**|**Description**|
|---|---|---|
|GET|/api/health|Health check — confirms backend + Neo4j connection|
|POST|/api/chat|Main agent endpoint. Body:{"query": "..."}.|
|||Returns: answer + intent + graph data|
|GET|/api/prices|All recent price observations. Query params:?|
|||county=&breed=|
|GET|/api/|Slaughterhouse directory. Query param:?|
||slaughterhouses|halal_only=true|
|GET|/api/feed|Feed product prices. Query param:?county=|
|GET|/api/nrv|Net Realizable Value ranking. Params:?|
|||breed=&age_class=&origin_county=|
|GET|/api/masumi/|Full 5-step Masumi agent-to-agent demo flow|
||demo||



POST /api/masumi/ Paid Masumi service endpoint — receives payment ref, returns Collateral Valuation Report report 

## **Example: /api/chat** 

curl -X POST https://your-backend.railway.app/api/chat \ 

- -H "Content-Type: application/json" \ 

- -d '{"query": "What is the price of a Boran steer in Kajiado this month?"}' 

{ "answer": "Based on NDMA data, a Store (2–3yr) Boran steer in Kajiado was priced at approximately KES 45,000–48,000 per head at Kiserian market as of May 2026 (NDMA May 2026 bulletin). This represents a slight increase from the April figure of KES 43,500.", "intent": "price_lookup", "entities": {"breed": "Boran", "age_class": "Store(2-3yr)", "county": "Kajiado"}, "graph_data": [...], "model": "Qwen/Qwen2.5-7B-Instruct", "query_description": "Price lookup: Boran Store(2-3yr) in Kajiado" } 

## **9. Agent Economy — Masumi** 

Masumi enables MifugoIQ to operate as a **paid B2B intelligence service** on the Cardano blockchain — other AI agents (lender bots, cooperative procurement agents, export sourcing agents) can pay per query without any human in the loop. 

## **9.1 Registered Services & Pricing** 

|**Service**|**Price**|**Inputs**|**Output**|
|---|---|---|---|
||**(USDM)**|||
|Collateral|$0.50|breed, age class,|Per-head price, NRV,|
|Valuation Report||head count, county|environmental risk flag, suggested|
||||LTV %|
|Finishing Cost|$0.25|breed, head count,|Total feed cost, cost-per-kg-gained,|
|Report||days, county|margin estimate|
|NRV Logistics|$0.25|breed, age class,|Ranked market comparison|
|Report||origin county|(gross price<br>transport cost)<br>−|



## **9.2 Agent-to-Agent Demo Flow** 

The Masumi demo (/api/masumi/demo) simulates the exact Section 4.6.2 scenario from the project outline — end-to-end in five visible steps: 

- Step 1: AgriFin Lender Agent receives loan application 

- ("15 Boran steers, 2–3 years, Kajiado") 

- │ 

Step 2: Lender Agent requests payment invoice from MifugoIQ 

   - → payment_ref: "DEMO-COLLATERAL-001", amount: 0.50 USDM 

- │ 

Step 3: Payment verified (dev mode: auto-confirmed; live mode: on-chain) 

- │ 

## Step 4: MifugoIQ generates Collateral Valuation Report 

   - → per_head_price_kes: 45,000 

   - → total_gross_kes: 675,000 

   - → net_realizable_value_kes: 637,500 

   - → underwriting_recommendation: "Moderate Risk — Standard LTV applies" 

- │ 

Step 5: Lender Agent computes loan decision 

- → LTV 65% → loan_limit_kes: 414,375 → DECISION: APPROVE 

**Why this matters commercially:** This is MifugoIQ's primary B2B revenue model from day one — financial institutions as paying agent-consumers, rather than relying on lowwillingness-to-pay end users. The same Masumi rail Phase 1 uses for per-report payments is the exact infrastructure Phase 2's escrow marketplace reuses. 

## **9.3 Dev Mode vs Live Mode** 

|**.3 Dev**|**Mode vs Live Mode**||
|---|---|---|
|**Mode**|**Setting**|**Behaviour**|
|Dev /|MASUMI_DEV_MODE=true,|Payment steps are simulated; full 5-step|
|Demo|MASUMI_API_KEYblank|demo still runs; safe for live demo without|
|||funded wallet|
|Live|MASUMI_API_KEY=<key>,|Real on-chain payments via Cardano; agent|
||MASUMI_DEV_MODE=false|auto-registered on Masumi network at startup|



## **10. Frontend — Lovable** 

The Lovable web app at mifugoiq1.lovable.app is the primary user-facing interface. The lovable/ folder contains three files to paste directly into the Lovable project editor. 

## **Application Surfaces** 

**Surface Component What It Shows Chat** Chat.tsx Bilingual conversational interface with suggested query chips; connects to /api/chat; shows intent tag and source on every answer **Price Explorer** (built in County-level price heatmap and trend charts driven by Lovable) /api/prices **Value Chain** (built in Interactive Neo4j graph visualisation — selecting a **Graph View** Lovable) county highlights its connected markets, slaughterhouses, feed suppliers, transporters **Directories** (built in Searchable/filterable Slaughterhouse (Halal filter), Lovable) Feed Supplier, and Transporter lists from /api/slaughterhouses and /api/feed **Masumi Demo** MasumiDemo. Interactive UI showing the full 5-step agent-to-agent tsx payment flow with live results 

## **Design Principles** 

- **Mobile-first:** Optimised for basic smartphones on limited data — most herders and SACCO field officers access via mobile 

- **Bilingual:** English and Kiswahili throughout all UI text and agent responses 

- **Trust through transparency:** Every data point shown carries a visible source and date tag 

## **Connecting Lovable to the Backend** 

## In your Lovable project: **Project Settings → Environment Variables → Add:** 

VITE_API_URL = https://your-backend.railway.app 

## **11. Deployment & Setup** 

## **Prerequisites** 

- Neo4j AuraDB instance (free tier works) with the graph seeded from Cypher.txt 

- Featherless API key (fl-...) from featherless.ai 

- Railway or Render account for backend hosting 

- Lovable project at mifugoiq1.lovable.app 

## **Step 1 — Seed the Neo4j Graph** 

1. Go to console.neo4j.io → open your instance → **Query** 

2. Copy the contents of Cypher.txt and run it in the Neo4j Browser 

3. Verify with: MATCH (n) RETURN labels(n), count(n) ORDER BY count(n) DESC 

## **Step 2 — Configure Environment Variables** 

Copy backend/.env.example to backend/.env and fill in: 

NEO4J_URI=neo4j+s://XXXXXXXX.databases.neo4j.io   # From AuraDB console → Connect 

NEO4J_USER=neo4j NEO4J_PASSWORD=your-aura-password 

FEATHERLESS_API_KEY=fl-your-key-here               # From featherless.ai → API Keys FEATHERLESS_MODEL=Qwen/Qwen2.5-7B-Instruct 

MASUMI_API_KEY=                                    # Leave blank for demo mode MASUMI_DEV_MODE=true 

MIFUGOIQ_CALLBACK_URL=https://your-backend.railway.app/api/masumi/report 





Repository Structure
MifugoIQ

April_NDMA                            -  Raw/Processed NDMA Early Warning Bulletins (April 2026)

May_NDMA/                             -  Raw/Processed NDMA Early Warning Bulletins (May 2026)

June_NDMA/                            -  Raw/Processed NDMA Early Warning Bulletins (June 2026)

Approvedexportslaughterhouses.csv     -  DVS & Halal-certified abattoir directory

feed_prices_mkulima_bora.csv.csv      -  Feed, fodder, and supplement pricing benchmarks

friction_metrics.csv.csv              -  Biophysical proxies (VCI, water trekking distances)

marketandzone.csv                     -  Geographic mapping of markets to livelihood zones

prices.csv                            -  Time-series livestock and commodity price observations

transport_benchmarks.csv.csv          -  Logistics and trucking cost benchmarks

Cypher.txt                            -  Master Neo4j schema, constraints, and seeding scripts

.gitignore                            -  Standard Python/Env ignore rules

