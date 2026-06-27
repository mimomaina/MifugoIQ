"""
Cypher query templates for MifugoIQ GraphRAG.
Each function returns (cypher_string, params_dict).
"""

def price_lookup(breed: str, age_class: str, county: str) -> tuple[str, dict]:
    """Latest price for a specific breed/age class in a county."""
    return (
        """
        MATCH (a:AnimalClass)-[:OF_BREED]->(b:Breed)
        MATCH (a)-[:PRICED_AT]->(p:PriceObservation)-[:RECORDED_AT]->(m:Market)-[:LOCATED_IN]->(c:County)
        WHERE toLower(b.name) CONTAINS toLower($breed)
          AND toLower(a.ageClass) CONTAINS toLower($age_class)
          AND toLower(c.name) = toLower($county)
        RETURN b.name AS breed, a.ageClass AS ageClass, m.name AS market,
               p.priceKES AS priceKES, p.date AS date, p.source AS source
        ORDER BY p.date DESC LIMIT 5
        """,
        {"breed": breed, "age_class": age_class, "county": county},
    )


def price_comparison(breed: str, age_class: str, county_a: str, county_b: str) -> tuple[str, dict]:
    """Compare prices between two counties."""
    return (
        """
        MATCH (a:AnimalClass)-[:OF_BREED]->(b:Breed)
        MATCH (a)-[:PRICED_AT]->(p:PriceObservation)-[:RECORDED_AT]->(m:Market)-[:LOCATED_IN]->(c:County)
        WHERE toLower(b.name) CONTAINS toLower($breed)
          AND toLower(a.ageClass) CONTAINS toLower($age_class)
          AND (toLower(c.name) = toLower($county_a) OR toLower(c.name) = toLower($county_b))
        RETURN c.name AS county, b.name AS breed, a.ageClass AS ageClass,
               m.name AS market, p.priceKES AS priceKES, p.date AS date, p.source AS source
        ORDER BY c.name, p.date DESC LIMIT 10
        """,
        {"breed": breed, "age_class": age_class, "county_a": county_a, "county_b": county_b},
    )


def net_realizable_value(breed: str, age_class: str, origin_county: str) -> tuple[str, dict]:
    """Best net price after transport — the flagship NRV query."""
    return (
        """
        MATCH (a:AnimalClass)-[:OF_BREED]->(b:Breed)
        MATCH (a)-[:PRICED_AT]->(p:PriceObservation)-[:RECORDED_AT]->(m:Market)-[:LOCATED_IN]->(dest:County)
        MATCH (t:Transporter)-[:SERVICES]->(origin:County {name: $origin_county})
        MATCH (t)-[:SERVICES]->(dest)
        WHERE toLower(b.name) CONTAINS toLower($breed)
          AND toLower(a.ageClass) CONTAINS toLower($age_class)
          AND p.date >= date('2026-01-01')
        RETURN m.name AS market, dest.name AS destCounty,
               p.priceKES AS grossPrice, t.costBenchmarkKES AS transportCost,
               (p.priceKES - t.costBenchmarkKES) AS netPrice,
               p.date AS date, p.source AS source, t.name AS transporter
        ORDER BY netPrice DESC LIMIT 5
        """,
        {"breed": breed, "age_class": age_class, "origin_county": origin_county},
    )


def halal_slaughterhouses(county: str = None) -> tuple[str, dict]:
    """Find Halal-certified abattoirs, optionally near a county."""
    if county:
        return (
            """
            MATCH (s:Slaughterhouse)-[:LOCATED_IN]->(c:County)
            WHERE s.halalCertified = true
            RETURN s.name AS name, c.name AS county, s.location AS location,
                   s.capacityHeadPerDay AS capacityPerDay, s.slaughterFeeKES AS feeKES,
                   s.halalCertified AS halal
            ORDER BY c.name LIMIT 10
            """,
            {},
        )
    return (
        """
        MATCH (s:Slaughterhouse)-[:LOCATED_IN]->(c:County)
        WHERE s.halalCertified = true
        RETURN s.name AS name, c.name AS county, s.location AS location,
               s.capacityHeadPerDay AS capacityPerDay, s.halalCertified AS halal
        ORDER BY c.name LIMIT 10
        """,
        {},
    )


def all_slaughterhouses() -> tuple[str, dict]:
    return (
        """
        MATCH (s:Slaughterhouse)-[:LOCATED_IN]->(c:County)
        RETURN s.name AS name, c.name AS county, s.location AS location,
               s.capacityHeadPerDay AS capacityPerDay, s.halalCertified AS halal,
               s.slaughterFeeKES AS feeKES
        ORDER BY c.name LIMIT 20
        """,
        {},
    )


def feed_costs(county: str) -> tuple[str, dict]:
    """Feed product prices available near a county."""
    return (
        """
        MATCH (f:FeedProduct)-[:SUPPLIED_BY]->(sup:FeedSupplier)
        RETURN f.name AS product, f.category AS category,
               f.priceKES AS priceKES, sup.name AS supplier, sup.type AS supplierType
        ORDER BY f.category, f.priceKES LIMIT 20
        """,
        {"county": county},
    )


def finishing_cost_estimate(head: int, days: int) -> tuple[str, dict]:
    """Rough finishing cost estimate from graph feed prices."""
    return (
        """
        MATCH (f:FeedProduct)
        RETURN f.name AS product, f.category AS category, f.priceKES AS priceKES
        ORDER BY f.category
        """,
        {"head": head, "days": days},
    )


def collateral_valuation(breed: str, age_class: str, head: int, county: str) -> tuple[str, dict]:
    """Full collateral valuation: prices + friction metrics + NRV."""
    return (
        """
        MATCH (a:AnimalClass)-[:OF_BREED]->(b:Breed)
        MATCH (a)-[:PRICED_AT]->(p:PriceObservation)-[:RECORDED_AT]->(m:Market)-[:LOCATED_IN]->(c:County)
        WHERE toLower(b.name) CONTAINS toLower($breed)
          AND toLower(a.ageClass) CONTAINS toLower($age_class)
          AND (toLower(c.name) = toLower($county) OR true)
        WITH b, a, p, m, c ORDER BY p.date DESC LIMIT 3
        OPTIONAL MATCH (origin:County {name: $county})-[:HAS_METRIC]->(fm:FrictionMetric)
        WHERE fm.type = 'Livestock Water Trek'
        WITH b, a, p, m, c, fm ORDER BY fm.date DESC LIMIT 1
        OPTIONAL MATCH (t:Transporter)-[:SERVICES]->(origin2:County {name: $county})
        RETURN b.name AS breed, a.ageClass AS ageClass,
               p.priceKES AS perHeadKES, $head AS headCount,
               (p.priceKES * $head) AS totalGrossKES,
               t.costBenchmarkKES AS transportCostPerHead,
               ((p.priceKES - coalesce(t.costBenchmarkKES, 0)) * $head) AS netRealizableValueKES,
               fm.value AS waterTrekKm,
               CASE
                 WHEN fm.value > 4.5 THEN 'High Risk — reduce LTV (herd caloric stress likely)'
                 WHEN fm.value > 3.0 THEN 'Moderate Risk — standard LTV applies'
                 ELSE 'Low Risk — premium LTV eligible'
               END AS underwritingFlag,
               p.date AS priceDate, p.source AS source, m.name AS market
        LIMIT 1
        """,
        {"breed": breed, "age_class": age_class, "head": head, "county": county},
    )


def friction_metrics(county: str) -> tuple[str, dict]:
    """Environmental risk metrics for a county."""
    return (
        """
        MATCH (c:County {name: $county})-[:HAS_METRIC]->(f:FrictionMetric)
        RETURN f.type AS metricType, f.value AS value, f.unit AS unit,
               f.date AS date, f.source AS source
        ORDER BY f.date DESC, f.type LIMIT 10
        """,
        {"county": county},
    )


def all_prices_recent() -> tuple[str, dict]:
    """All recent price observations — overview."""
    return (
        """
        MATCH (a:AnimalClass)-[:OF_BREED]->(b:Breed)
        MATCH (a)-[:PRICED_AT]->(p:PriceObservation)-[:RECORDED_AT]->(m:Market)-[:LOCATED_IN]->(c:County)
        WHERE p.date >= date('2026-01-01')
        RETURN b.name AS breed, a.ageClass AS ageClass, c.name AS county,
               m.name AS market, p.priceKES AS priceKES, p.date AS date, p.source AS source
        ORDER BY p.date DESC, c.name LIMIT 30
        """,
        {},
    )
