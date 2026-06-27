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

