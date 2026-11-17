"""
GRAPH LAYER (Neo4j)
-------------------
Stores entity relations from your PDFs:
    (Entity {name: "alice"}) -[RELATION {type: "reports to", chunk_id, source}]-> (Entity {name: "bob"})

chunk_id is the same ID used for the chunk in Pinecone ("<filename>-<index>").

Functions used by ML/retrieval.py:
    init_graph()                              -> check connection, create constraint (startup)
    add_document_triples(client, src, chunks) -> extract and store relations (upload)
    graph_lookup(question, hops, ...)         -> find linked chunk IDs and readable facts (ask)
"""

import os
import re
import json
import certifi
from collections import Counter
from neo4j import GraphDatabase, TrustCustomCAs
from dotenv import load_dotenv
from neo4j import GraphDatabase
from google.genai import types
import time



load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI").replace("neo4j+s://", "neo4j://")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
EXTRACT_MODEL = "gemini-3.5-flash-lite"

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
    encrypted=True,
    trusted_certificates=TrustCustomCAs(certifi.where()),
)
# ---------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------

def init_graph():
    """Check the connection and make entity names unique."""
    driver.verify_connectivity()
    with driver.session() as session:
        session.run(
            "CREATE CONSTRAINT entity_name IF NOT EXISTS "
            "FOR (e:Entity) REQUIRE e.name IS UNIQUE"
        )
    print("🕸️ Neo4j graph ready")


def close_graph():
    driver.close()


def norm(text):
    """Lowercase, strip punctuation, collapse spaces: 'Alice,' == 'alice'."""
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", str(text).lower()).split())


# ---------------------------------------------------------------------
# UPLOAD: extract relations with Gemini and store them
# ---------------------------------------------------------------------
EXTRACT_PROMPT = (
    "Extract the key entity relationships stated in the text below.\n"
    "Return ONLY a JSON array of objects with keys: subject, relation, object.\n"
    "Rules:\n"
    "- Entities are short noun phrases (people, organizations, products, policies, places, concepts).\n"
    "- Relations are short verb phrases such as 'reports to', 'owns', 'applies to', 'located in'.\n"
    "- Use only facts explicitly stated in the text. Maximum 8 items.\n"
    "- If there are no clear relationships, return [].\n\n"
    "TEXT:\n"
)


EXTRACT_MODELS = ["gemini-3.5-flash-lite", "gemini-3.6-flash"]  # first choice, then fallback
RETRY_WAITS = [2, 5, 10]  # seconds between attempts
def _generate_with_retry(client, prompt):
    """Retry busy-model errors (429/503), then try the fallback model."""
    last_error = None
    for model in EXTRACT_MODELS:
        for wait in [0] + RETRY_WAITS:
            if wait:
                time.sleep(wait)
            try:
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0,
                    ),
                )
            except Exception as e:
                last_error = e
                msg = str(e)
                if "503" in msg or "429" in msg or "UNAVAILABLE" in msg or "RESOURCE_EXHAUSTED" in msg:
                    continue  # temporary: wait and try again
                raise  # anything else (bad key, bad request) fails immediately
    raise last_error


def extract_triples(client, chunk):
    """Ask Gemini for (subject, relation, object) triples from one chunk."""
    response = _generate_with_retry(client, EXTRACT_PROMPT + chunk)
    data = json.loads(response.text)
    clean = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and all(k in item for k in ("subject", "relation", "object")):
                s, r, o = norm(item["subject"]), norm(item["relation"]), norm(item["object"])
                if s and r and o and s != o:
                    clean.append((s, r, o))
    return clean


def _replace_source(tx, source, rows):
    """Remove this file's old relations, then write the new ones."""
    tx.run("MATCH ()-[r:RELATION {source: $source}]->() DELETE r", source=source)
    tx.run("MATCH (e:Entity) WHERE NOT (e)--() DELETE e")
    if rows:
        tx.run(
            """
            UNWIND $rows AS row
            MERGE (s:Entity {name: row.subject})
            MERGE (o:Entity {name: row.object})
            CREATE (s)-[:RELATION {type: row.relation, chunk_id: row.chunk_id, source: $source}]->(o)
            """,
            rows=rows,
            source=source,
        )


def add_document_triples(client, source, chunks):
    """
    Extract relations for every chunk and store them.
    Re-uploading the same file replaces its old relations.
    One Gemini call per chunk. A failed chunk is skipped, not fatal.
    """
    rows = []
    for i, chunk in enumerate(chunks):
        try:
            for s, r, o in extract_triples(client, chunk):
                rows.append({
                    "subject": s,
                    "relation": r,
                    "object": o,
                    "chunk_id": f"{source}-{i}",  # must match the Pinecone record ID
                })
        except Exception as e:
            print(f"⚠️ Graph extraction failed for chunk {i}: {e}")

    with driver.session() as session:
        session.execute_write(_replace_source, source, rows)
    return len(rows)


# ---------------------------------------------------------------------
# QUERY: find entities in the question and walk their relations
# ---------------------------------------------------------------------
def find_entities(question):
    """Entity names that appear as whole words in the question."""
    q = f" {norm(question)} "
    with driver.session() as session:
        result = session.run(
            """
            MATCH (e:Entity)
            WHERE size(e.name) >= 3 AND $q CONTAINS (' ' + e.name + ' ')
            RETURN e.name AS name
            """,
            q=q,
        )
        return [row["name"] for row in result]


def graph_lookup(question, hops=1, max_facts=15, limit=50):
    """
    Returns (chunk_ids, facts):
      chunk_ids -> IDs of chunks linked to the matched relations, most-connected first
      facts     -> readable lines like "alice -[reports to]-> bob"
    """
    names = find_entities(question)
    if not names:
        return [], []

    frontier = set(names)
    visited = set(names)
    chunk_counts = Counter()
    facts, seen = [], set()

    with driver.session() as session:
        for _ in range(hops):
            if not frontier:
                break
            result = session.run(
                """
                MATCH (a:Entity)-[r:RELATION]->(b:Entity)
                WHERE a.name IN $names OR b.name IN $names
                RETURN a.name AS s, r.type AS rel, b.name AS o, r.chunk_id AS cid
                LIMIT $limit
                """,
                names=list(frontier),
                limit=limit,
            )
            next_frontier = set()
            for row in result:
                line = f"{row['s']} -[{row['rel']}]-> {row['o']}"
                if line not in seen:
                    seen.add(line)
                    facts.append(line)
                chunk_counts[row["cid"]] += 1
                next_frontier.update([row["s"], row["o"]])
            frontier = next_frontier - visited
            visited |= next_frontier

    chunk_ids = [cid for cid, _ in chunk_counts.most_common()]
    return chunk_ids, facts[:max_facts]