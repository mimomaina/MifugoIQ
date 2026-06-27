"""Neo4j AuraDB connection wrapper for MifugoIQ."""
import os
from neo4j import GraphDatabase
from typing import Optional

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        uri = os.environ["NEO4J_URI"]
        user = os.environ["NEO4J_USER"]
        password = os.environ["NEO4J_PASSWORD"]
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver

def run_query(cypher: str, params: dict = None) -> list[dict]:
    """Execute a Cypher query and return list of record dicts."""
    driver = get_driver()
    params = params or {}
    with driver.session() as session:
        result = session.run(cypher, **params)
        return [dict(record) for record in result]

def close():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
