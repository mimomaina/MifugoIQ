# MifugoIQ: Knowledge-Graph-Powered Market Intelligence Engine

Market Intelligence & Collateral Valuation Architecture
---

## 1. Executive Summary
MifugoIQ is an enterprise-grade, knowledge-graph-powered intelligence layer designed to map, structure, and query the entirety of Kenya’s beef and cattle value chain. By integrating fragmented institutional data into a unified Neo4j graph database and exposing it via a GraphRAG-enabled conversational agent, MifugoIQ provides authoritative, location-specific, and breed-specific market intelligence. 

This repository documents the foundational data engineering, domain ontology, and graph architecture required to solve critical gaps in agricultural finance (AgriFin)—specifically the inability of financial institutions to underwrite asset-backed loans against livestock collateral due to a lack of defensible, real-time valuation metrics.

---

## 2. Problem Statement: Systemic Information Asymmetry
Kenya’s cattle economy represents hundreds of billions of shillings annually and serves as the primary economic backbone for millions of pastoralist and smallholder households. Despite its scale, the value chain operates on systemic information asymmetry, fragmented data, and informal price discovery. 

At almost every handoff between value chain stages, critical data is lost, siloed, or inaccessible:

*   **Financial Institutions & Insurers (The AgriFin Gap):** Microfinance Institutions (MFIs), SACCOs, and commercial banks cannot underwrite asset-backed loans against livestock collateral. There is no authoritative, current, or queryable price reference to calculate the Net Realizable Value (NRV) of a herd, rendering livestock an "invisible" asset class for formal credit.
*   **Breeders & Herders:** Producers sell into primary auctions based on informal broker quotes, lacking benchmark data for comparable animals (by breed, age, weight, and body condition) across neighboring counties or terminal markets.
*   **Finishers & Feedlot Operators:** Operators cannot systematically compare feed, fodder, and supplement costs across suppliers. Consequently, the finishing-cost-per-kilogram-gained remains an estimate, undermining margin modeling and working capital applications.
*   **Slaughterhouses & Processors:** Facility capacities, slaughter fees, and critical export-enabling credentials (e.g., Halal certification status via DVS or SUPKEM) are scattered across disparate county records and physical registers, with no centralized digital directory.
*   **Logistics & Transporters:** Livestock haulage is highly informal. Pricing varies by relationship rather than standardized distance/load metrics, with zero visibility or accountability for transit welfare and shrinkage.

---

## 3.  Data & Graph Architecture
The current repository represents the completion of the Data Ingestion and Ontology Mapping milestone. We have successfully extracted, normalized, and loaded Tier 1 and Tier 2 institutional datasets into a production-grade Neo4j graph schema.

### 3.1 Ingested Data Sources
*   **NDMA Early Warning Bulletins (Kajiado County - Feb, Apr, May 2026):** Extracted time-series price observations for cattle and goats across specific livelihood zones (Pastoral, Agro-Pastoral, Mixed Farming), alongside critical biophysical friction metrics (Vegetation Condition Index, livestock water trekking distances, and body condition scores).
*   **DVS Export Slaughterhouse Registry:** Ingested the official directory of government-approved export abattoirs (e.g., Kenya Meat Commission, Farmers Choice, Quality Meat Packers), including location data, capacity indicators, and Halal certification status.
*   **Feed & Logistics Benchmarks:** Seeded baseline nodes for feed products (e.g., dairy meal, mineral licks) and regional transport cost benchmarks to enable Net Realizable Value (NRV) calculations.

### 3.2 Knowledge Graph Ontology (Neo4j)
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

#### Core Relationship Types (Edges)
| Relationship Pattern | Business Logic & Traversal Purpose |
| :--- | :--- |
| `(Market)-[:LOCATED_IN]->(County)` | Anchors price discovery to specific geographic and infrastructural zones. |
| `(AnimalClass)-[:OF_BREED]->(Breed)` | Links demographic cohorts to genetic lineages for breed-premium analysis. |
| `(AnimalClass)-[:PRICED_AT]->(PriceObservation)-[:RECORDED_AT]->(Market)` | Establishes the time-series financial valuation of specific asset classes. |
| `(Transporter)-[:SERVICES]->(County)` | Defines logistics coverage to calculate transport deductions for NRV. |
| `(County)-[:HAS_METRIC]->(FrictionMetric)` | Attaches environmental risk data (e.g., drought stress) to origin locations for risk-adjusted collateral valuation. |

---

## 4. Expected Graph Outputs & Flagship Queries
The architecture is specifically optimized for multi-hop GraphRAG reasoning. Below are the core Cypher query patterns that power the MifugoIQ intelligence layer.

<img width="1195" height="551" alt="image" src="https://github.com/user-attachments/assets/8c7e046d-8094-43ec-b6bf-e7d7540e66f9" />



### 4.1 Net Realizable Value (NRV) & Market Routing
*Used by financial underwriters and producers to determine the true value of an asset after logistical deductions.*

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
### 4.2 Risk-Adjusted Collateral Valuation
Used by AgriFin lenders to penalize or adjust Loan-to-Value (LTV) ratios based on localized environmental stress (e.g., severe drought or excessive water trekking indicating poor herd body condition).


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

### 5. Repository Structure
mifugo-iq-engine/

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
