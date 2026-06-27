## **MifugoIQ 🐄** 

## **Kenya's Cattle Value Chain — Knowledge-Graph Intelligence Engine** 

**Kenya AI Challenge 2026 · AgriFin Track · Mercy Corps AgriFin Network** Built for the Neo4j · Featherless · Lovable · Masumi technology tracks 


## **Table of Contents** 

1. The Problem 

2. What MifugoIQ Does 

3. System Architecture 

4. Repository Structure 

5. Data Layer — Sources & Ingestion 

6. Knowledge Graph — Neo4j Schema 7. GraphRAG Agent — Featherless 

8. Backend API 

9. Agent Economy — Masumi 

10. Frontend — Lovable 

11. Deployment & Setup 

12. Demo Script — Three Personas 13. Phase 2 Roadmap 

14. Team 

## **1. The Problem** 

Kenya's cattle economy is worth hundreds of billions of shillings annually and forms the primary livelihood for an estimated **6.36 million smallholder and pastoralist households** . The national herd stands at roughly 18 million cattle — yet at almost every handoff in the value chain, critical market information is lost, siloed, or inaccessible. 

The AgriFin gap is specific: **livestock pledged as loan collateral grew 53.6% year-onyear to June 2025** (Business Registration Services data), meaning lenders already want to lend against cattle. But appetite has outrun infrastructure. A SACCO loan officer in Kajiado evaluating a KSh 500,000 loan secured by 15 Boran steers has no defensible way to answer: 

_"What are these steers actually worth today, and what would I realistically recover if I had to call the loan?"_ 

The data to answer that question already exists — scattered across NDMA monthly bulletins, KNBS Statistical Abstracts, KMC reference prices, and DVS abattoir registers — but it is published as **static PDFs, on monthly cycles, siloed by institution** , and entirely unqueryable by a loan officer in a three-minute credit committee meeting. 

MifugoIQ is the connective tissue that fixes this. 

## **2. What MifugoIQ Does** 

MifugoIQ is a **knowledge-graph-powered AI agent** that maps the entire Kenyan cattle value chain into a single, continuously-updated, queryable intelligence layer. Anyone in the chain can ask a natural-language question in **English, Kiswahili, or Sheng** and get a grounded, sourced, location- and breed-specific answer. 

## **Core capabilities (Phase 1 — this build):** 

|**Query Type**|**Example**|**What the Agent Does**|
|---|---|---|
|**Price lookup**|"Bei ya ng'ombe wa Boran|Traverses AnimalClass<br>→|
||miaka 2 huko Kajiado?"|PriceObservation<br>Market<br>County;<br>→<br>→|
|||cites NDMA source and date|
|**Net**|"Where's my best market for|Multi-hop: prices across markets minus|
|**Realizable**|15 steers from Kajiado, all-|transporter cost benchmarks; ranked NRV|
|**Value**|in?"|table|
|**Collateral**|"Value 15 Boran steers, 2–3|Structured report: per-head price, NRV,|
|**valuation**|years, Kajiado, as loan|environmental risk flag, suggested LTV %|
||collateral"||
|**Halal facility**|"Nearest Halal-certified|Filters Slaughterhouse nodes by|
|**finder**|abattoir to Isiolo?"|halalCertified, returns name, county, fee,|
|||capacity|
|**Feed cost**|"Feed cost for 20 steers|FeedProduct × FeedSupplier × county;|
|**calculator**|over 90 days near|rough cost-per-kg-gained estimate|
||Machakos?"||
|**Risk**|"What's the drought risk for|Returns FrictionMetric (VCI, water trek|
|**assessment**|a herd in Kajiado this|distance) with underwriting flag|
||month?"||



## **What makes it different from a chatbot or a spreadsheet:** 

The agent never fabricates a number. Every price, fee, or cost it states is either returned by a live Cypher query against the Neo4j graph or explicitly flagged as unavailable. The graph 

traversal — not the LLM — does the reasoning. The LLM only composes the answer into natural language and translates it into the user's language. 

## **3. System Architecture** 

┌─────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                         │
│  NDMA Bulletins · KNBS Stats · DVS Registry · KMC Prices    │
│  Feed Manufacturer Lists · Transport Rate Surveys           │
└──────────────────────────┬──────────────────────────────────┘
                           │ CSV / PDF ingestion
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE GRAPH LAYER                      │
│                       Neo4j AuraDB                          │
│  County · Market · Breed · AnimalClass · PriceObservation   │
│  Slaughterhouse · Transporter · FeedProduct · FrictionMetric│
│  (Cypher.txt — schema + seed scripts)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ Cypher queries
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                GRAPHRAG REASONING LAYER                     │
│                  FastAPI Backend (backend/)                 │
│                                                             │
│  agent.py          — Intent detection → Cypher template     │
│                       → Neo4j → Featherless LLM → answer    │
│  cypher_templates.py — Parameterized query library          │
│  neo4j_client.py   — AuraDB connection wrapper              │
│  main.py           — 7 REST endpoints                       │
│  masumi.py         — Agent registration + payment rail      │
└────────────┬────────────────────────┬───────────────────────┘
             │ /api/chat              │ /api/masumi/report
             ▼                        ▼
┌────────────────────┐    ┌───────────────────────────────────┐
│  LOVABLE FRONTEND  │    │        MASUMI AGENT NETWORK       │
│  mifugoiq1.lovable │    │  MifugoIQ registered as paid      │
│  .app              │    │  agent service (ADA/USDM per      │
│                    │    │  report). Demo: AgriFin Lender    │
│  Chat.tsx          │    │  Agent → pays → gets Collateral   │
│  MasumiDemo.tsx    │    │  Valuation Report → loan decision │
│  mifugoiq.ts       │    │                                   │
└────────────────────┘    └───────────────────────────────────┘

## **Technology Stack:** 

## **Layer Technology** 

## **Role** 

Graph **Neo4j AuraDB** Stores the entire value chain as a database connected, queryable graph LLM serving **Featherless** Open-source LLM hosting; OpenAI(Qwen/Qwen2.5-7Bcompatible; no GPU management Instruct) Agent **Python / FastAPI** Intent detection, Cypher generation, framework answer composition Agent **Masumi** (Cardano) Agent-to-agent payment rail for B2B payments intelligence reports Frontend **Lovable** Deployed web app — chat UI, price explorer, Masumi demo 

## **4. Repository Structure** 

MifugoIQ/
│
├── 📁 April_NDMA/                              # NDMA Early Warning Bulletin — April 2026
├── 📁 May_NDMA/                                # NDMA Early Warning Bulletin — May 2026
├── 📁 June_NDMA/                               # NDMA Early Warning Bulletin — June 2026
│
├── 📄 prices.csv                               # Time-series livestock price observations
├── 📄 marketandzone.csv                        # Markets mapped to counties & livelihood zones
├── 📄 Approvedexportslaughterhouses.csv        # DVS-registered export abattoir directory
├── 📄 feed_prices_mkulima_bora.csv             # Feed & supplement pricing benchmarks
├── 📄 transport_benchmarks.csv                 # Livestock transport cost benchmarks
├── 📄 friction_metrics.csv                     # Biophysical risk metrics (VCI, water trek km, BCS)
│
├── 📄 Cypher.txt                               # ★ Master Neo4j schema, constraints & seed scripts
│
├── 📁 backend/                                 # ★ FastAPI backend — GraphRAG + Featherless + Masumi
│   ├── 📄 main.py                              # API server (7 endpoints)
│   ├── 📄 agent.py                             # GraphRAG pipeline (intent → Cypher → LLM → answer)
│   ├── 📄 cypher_templates.py                  # Parameterized Cypher query library
│   ├── 📄 neo4j_client.py                      # Neo4j AuraDB connection wrapper
│   ├── 📄 masumi.py                            # Agent registration, payments & demo flow
│   ├── 📄 requirements.txt                     # Python dependencies
│   ├── 📄 Procfile                             # Railway/Render deployment start command
│   └── 📄 .env.example                         # Environment variable template
│
├── 📁 lovable/                                 # ★ Lovable frontend integration files
│   ├── 📄 mifugoiq.ts                          # API service layer (paste → src/services/)
│   ├── 📄 Chat.tsx                             # Bilingual chat UI component
│   └── 📄 MasumiDemo.tsx                       # Interactive Masumi agent-to-agent demo
│
├── 📄 INTEGRATION_GUIDE.md                     # ★ Deployment & setup guide (keys, steps, debug)
├── 📄 .gitignore
└── 📄 README.md                                # This file

## **5. Data Layer — Sources & Ingestion** 

## **5.1 Data Sources** 

MifugoIQ does not generate new primary data. Its contribution is **connective tissue** — ingesting, normalising, linking, and making queryable what already exists in institutional datasets. 

**Tier** 

**Source** 

**What It Provides** 

**Files in Repo** 

|**Tier**|NDMA Monthly|County-level cattle|April_NDMA/,May_NDMA/,|
|---|---|---|---|
|**1**|Early Warning|prices by livelihood|June_NDMA/,prices.csv,|
||Bulletins|zone, body condition|friction_metrics.csv.csv|
|||scores, water trek||
|||distances (friction||
|||metrics)||
|**Tier**|DVS Export|Government-registered|Approvedexportslaughterhouse|
|**1**|Abattoir Register|slaughterhouses, Halal|s.csv|
|||certification status,||
|||county location||
|**Tier**|Kenya Meat|Reference slaughter|Seeded inCypher.txt|
|**2**|Commission|fees and processing||
||(KMC)|standards||
|**Tier**|Feed|Feed, fodder, and|feed_prices_mkulima_bora.csv|
|**2**|manufacturer|supplement prices per|.csv|
||price lists (Unga|kg/bag||
||Farm Care,|||
||Pembe, Sigma,|||
||Jubaili)|||
|**Tier**|Transport rate|Per-head livestock|transport_benchmarks.csv.csv|
|**3**|surveys /|haulage cost||
||agricultural news|benchmarks by route||
|**Tier**|Geographic /|Market-to-county-to-|marketandzone.csv|
|**3**|market directory|livelihood-zone||
|||mapping||



All figures are sourced, date-stamped, and flagged with a confidence level in the graph. Researched estimates are explicitly marked as such — **silent fabrication is never acceptable** . 

## **5.2 Ingestion Strategy** 

Data flows into Neo4j through three mechanisms: 

**1. Cypher.txt — master seed script** Contains all CREATE CONSTRAINT, CREATE INDEX, MERGE, and CREATE statements to build and populate the full graph schema from scratch. Run this in Neo4j Browser or Aura Console to rebuild the database at any time. 

**2. CSV ingestion (Cypher LOAD CSV)** The structured CSVs (prices.csv, 

marketandzone.csv, etc.) are loaded via LOAD CSV WITH HEADERS statements in Cypher.txt, normalising field names to the graph's controlled vocabulary before creating nodes and relationships. 

**3. Manual enrichment** Slaughterhouse, feedlot, buyer, and export market nodes that cannot be fully populated from CSVs are seeded directly in Cypher.txt with MERGE patterns, ensuring every demo query has a grounded answer even where public data is sparse. 

## **5.3 MVP Geographic Scope** 

The seeded dataset covers the following counties and markets, chosen to span all major regions while remaining completeable in 48 hours: 

|**Region**|**Counties**|**Markets**|
|---|---|---|
|Nairobi / Central|Nairobi, Kajiado|Dagoretti, Kiserian|
|Rift Valley|Nakuru, Narok|Nakuru Market, Ewaso Ngiro|
|Eastern|Machakos|Kangundo|
|Northern / ASAL|Garissa, Isiolo|Garissa, Isiolo|



**Breeds seeded:** Boran, Small East African Zebu, Sahiwal-cross, Friesian-cross **Age classes:** Weaner (1–2yr), Store (2–3yr), Mature/Finished (3+yr) 

## **6. Knowledge Graph — Neo4j Schema** 

## **6.1 Node Labels** 

|**Node Label**|**Represents**|**Key Properties**|
|---|---|---|
|County|One of Kenya's 47|name,region|
||counties||
|Market|Primary livestock auction|name,marketType,livelihoodZone,|
||point|frequency|
|Breed|Cattle breed or cross|name,originType(Indigenous /|
|||Improved Beef / Dairy)|
|AnimalClass|Breed × age class × sex|ageClass,sex,|
||cohort|bodyConditionScore,|
|||liveweightRangeKg|
|PriceObserva|Time-stamped price for a|priceKES,minKES,maxKES,date,|
||cohort at a market||



tion source, unit Slaughterhou Abattoir / processing name, county, capacityHeadPerDay, se facility halalCertified, slaughterFeeKES Transporter Livestock / meat haulage name, vehicleType, provider costBenchmarkKES, coverageCounties FeedProduct Feed, fodder, or name, category, priceKES, cpPct, supplement item caPct, pPct FeedSupplier Feed manufacturer or name, type, county agrovet FrictionMetr Biophysical risk indicator type (Water Trek / VCI / BCS), value, ic unit, date, source Feedlot Cattle finishing operation name, county, capacityHead, finishingPeriodDays Buyer Demand-side actor type (butchery / supermarket / hotel / exporter), county, gradeDemand ExportMarket Export destination country, productType, requirements (e.g. Halal mandatory) 

## **6.2 Relationship Types** 

**Relationshi Pattern p** LOCATED_I `(Market|Slaughterhouse|Feedlot|FeedSupplier|` N `Buyer)→(County)` OF_BREED `(AnimalClass)→(Breed)` 

**Business Logic** 

Anchors every actor to a county for geographic reasoning Links price cohorts to breed genetics for premium analysis 

PRICED_AT `(AnimalClass)→(PriceObservation)` 

RECORDED_ `(PriceObservation)→(Market)` AT 

SERVICES `(Transporter)→(County)` 

HAS_METRI `(County)→(FrictionMetric)` C 

SUPPLIED_ `(FeedProduct)→(FeedSupplier)` BY 

FEEDS_WIT `(Feedlot)→(FeedProduct)` H 

CERTIFIED `(Slaughterhouse)→(ExportMarket)` _AS 

EXPORTS_T `(Slaughterhouse|Buyer)→(ExportMarket)` O 

Attaches timestamped price observations to cohorts 

Locates each price observation at its source market 

Defines logistics coverage for NRV transport deductions 

Attaches environment al risk data for riskadjusted LTV 

Powers feed cost sourcing queries 

Links finishing operations to their input rations 

Maps export eligibility (Halal, DVS grade) 

Traces export channel relationships 

## **6.3 Flagship Cypher Queries** 

## **Net Realizable Value — the core multi-hop query:** 

MATCH (a:AnimalClass {ageClass: 'Store(2-3yr)', sex: 'Male'})-[:OF_BREED]->(:Breed {name: 'Boran'}) 

MATCH (a)-[:PRICED_AT]->(p:PriceObservation)-[:RECORDED_AT]->(m:Market)- 

[:LOCATED_IN]->(dest:County) 

MATCH (t:Transporter)-[:SERVICES]->(origin:County {name: 'Kajiado'}) 

MATCH (t)-[:SERVICES]->(dest) 

WHERE p.date >= date('2026-04-01') 

RETURN m.name AS market, p.priceKES AS grossPrice, 

t.costBenchmarkKES AS transportCost, 

- (p.priceKES - t.costBenchmarkKES) AS netRealizableValue 

ORDER BY netRealizableValue DESC LIMIT 3; 

## **Risk-adjusted collateral underwriting:** 

MATCH (c:County {name: 'Kajiado'})-[:HAS_METRIC]->(f:FrictionMetric {type: 'Livestock Water Trek'}) 

WHERE f.date >= date('2026-02-01') RETURN c.name AS county, f.value AS waterTrekKm, 

CASE 

WHEN f.value > 4.5 THEN 'High Risk — Reduce LTV (herd caloric stress likely)' WHEN f.value > 3.0 THEN 'Moderate Risk — Standard LTV applies' ELSE 'Low Risk — Premium LTV eligible' 

END AS underwritingRecommendation; 

## **Halal abattoir finder:** 

MATCH (s:Slaughterhouse)-[:LOCATED_IN]->(c:County) WHERE s.halalCertified = true RETURN s.name, c.name AS county, s.capacityHeadPerDay, s.slaughterFeeKES ORDER BY c.name; 

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






