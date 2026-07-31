import os
import re
import sqlite3
import struct
from typing import Dict, List
import numpy as np
import ollama

from modules.config import EMBEDDING_MODEL
from modules.text_utils import normalize_text

DB_PATH = "data/clinical_knowledge.db"
GUIDELINES_DIR = "clinical_guidelines"

# Static Fallback Knowledge Base (in case DB or Ollama is down)
_KNOWLEDGE_BASE = [
    {
        "title": "Sore throat overview",
        "source": "CDC",
        "url": "https://www.cdc.gov/groupastrep/diseases-public/strep-throat.html",
        "snippet": "Most sore throats are viral; antibiotics are only effective for bacterial infections confirmed by a clinician.",
        "keywords": ["sore throat", "strep", "antibiotic", "throat"],
    },
    {
        "title": "Chest pain emergency warning",
        "source": "NIH",
        "url": "https://www.nhlbi.nih.gov/health/heart-attack",
        "snippet": "Chest pain with shortness of breath can be a medical emergency and requires urgent evaluation.",
        "keywords": ["chest pain", "shortness of breath", "difficulty breathing"],
    },
    {
        "title": "Abdominal pain red flags",
        "source": "WHO",
        "url": "https://www.who.int/news-room/fact-sheets",
        "snippet": "Severe abdominal pain with black stools or vomiting blood can indicate serious internal bleeding.",
        "keywords": ["abdominal pain", "black stools", "vomiting blood"],
    },
    {
        "title": "Fever guidance",
        "source": "CDC",
        "url": "https://www.cdc.gov/flu/symptoms/index.html",
        "snippet": "Fever can indicate infection; persistent or high fever warrants medical evaluation.",
        "keywords": ["fever", "infection"],
    },
]

# Static fallback index
_FALLBACK_INDEX = {}
for entry in _KNOWLEDGE_BASE:
    for keyword in entry["keywords"]:
        key_norm = keyword.lower().strip()
        if key_norm not in _FALLBACK_INDEX:
            _FALLBACK_INDEX[key_norm] = []
        _FALLBACK_INDEX[key_norm].append(entry)


def serialize_vector(vec: list) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def deserialize_vector(blob: bytes) -> list:
    num_floats = len(blob) // 4
    return list(struct.unpack(f"{num_floats}f", blob))


def get_embedding(text: str) -> list:
    try:
        if hasattr(ollama, "embed"):
            response = ollama.embed(model=EMBEDDING_MODEL, input=text)
            if "embeddings" in response:
                return response["embeddings"][0]
            elif "embedding" in response:
                return response["embedding"]
        response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
        return response["embedding"]
    except Exception as e:
        print(f"[RAG Warning] Embedding generation failed for text: '{text[:20]}...'. Error: {e}")
        # Return a dummy list of 768 floats (nomic-embed-text size)
        return [0.0] * 768


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            url TEXT,
            content TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    return conn, cursor


def parse_markdown_guideline(file_path: str):
    """Parses markdown guidelines into chunks with metadata."""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract source & url from top metadata
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(file_path)

    source_match = re.search(r"\*\*Source:\*\*\s*(.+)$", content, re.MULTILINE)
    source = source_match.group(1).strip() if source_match else "Official Guideline"

    url_match = re.search(r"\*\*URL:\*\*\s*(.+)$", content, re.MULTILINE)
    url = url_match.group(1).strip() if url_match else ""

    # Split content by paragraphs or headers
    chunks = []
    sections = re.split(r"\n\n+", content)
    for sec in sections:
        sec = sec.strip()
        # Skip headers and metadata lines in chunks
        if not sec or sec.startswith("#") or sec.startswith("**Source:") or sec.startswith("**URL:"):
            continue
        chunks.append(sec)
        
    return [{
        "source": source,
        "title": title,
        "url": url,
        "content": chunk
    } for chunk in chunks]


def ingest_guidelines():
    """Bootstrap ingestion of local guidelines if the DB is empty."""
    try:
        conn, cursor = init_db()
        cursor.execute("SELECT COUNT(*) FROM knowledge_chunks")
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return
            
        print("[RAG Ingestion] Initializing vector database from clinical_guidelines...")
        if not os.path.exists(GUIDELINES_DIR):
            print(f"[RAG Warning] Guidelines directory '{GUIDELINES_DIR}' not found.")
            conn.close()
            return

        for filename in os.listdir(GUIDELINES_DIR):
            if filename.endswith(".md"):
                file_path = os.path.join(GUIDELINES_DIR, filename)
                chunks_data = parse_markdown_guideline(file_path)
                
                for chunk in chunks_data:
                    vec = get_embedding(chunk["content"])
                    # Check if we returned a dummy vector (means embedding failed)
                    if vec == [0.0] * 768:
                        continue
                    cursor.execute("""
                        INSERT INTO knowledge_chunks (source, title, url, content, embedding)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        chunk["source"],
                        chunk["title"],
                        chunk["url"],
                        chunk["content"],
                        serialize_vector(vec)
                    ))
        conn.commit()
        conn.close()
        print("[RAG Ingestion] Vector database initialized successfully.")
    except Exception as e:
        print(f"[RAG Ingestion Error] Failed to bootstrap vector DB: {e}")


if __name__ == "__main__":
    ingest_guidelines()


def cosine_similarity(v1: list, v2: list) -> float:
    arr1 = np.array(v1)
    arr2 = np.array(v2)
    dot = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


def retrieve_evidence(query: str, max_results: int = 3) -> Dict[str, object]:
    normalized = normalize_text(query)
    
    # Try dynamic vector search using SQLite and Ollama Embeddings
    try:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError("Database file missing")
            
        # Get query embedding
        query_vec = get_embedding(query)
        # If dummy vector returned, fall back to keyword match
        if query_vec == [0.0] * 768:
            raise ValueError("Failed to get query embedding")
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT source, title, url, content, embedding FROM knowledge_chunks")
        rows = cursor.fetchall()
        conn.close()
        
        scored = []
        for row in rows:
            source, title, url, content, emb_blob = row
            chunk_vec = deserialize_vector(emb_blob)
            sim = cosine_similarity(query_vec, chunk_vec)
            # Threshold score to filter out irrelevant noise
            if sim > 0.45:
                scored.append({
                    "score": sim,
                    "entry": {
                        "source": source,
                        "title": title,
                        "url": url,
                        "snippet": content
                    }
                })
                
        scored.sort(key=lambda item: item["score"], reverse=True)
        evidence = [item["entry"] for item in scored[:max_results]]
        
        if evidence:
            return {
                "evidence": evidence,
                "used": True,
                "engine": "vector_database"
            }
    except Exception as e:
        print(f"[RAG Warning] Vector search failed: {e}. Falling back to static keyword index.")
        
    # Fallback keyword index (inverted index)
    entry_scores: Dict[int, Dict[str, object]] = {}
    for keyword, entries in _FALLBACK_INDEX.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", normalized):
            for entry in entries:
                entry_id = id(entry)
                if entry_id not in entry_scores:
                    entry_scores[entry_id] = {"score": 0, "entry": entry}
                entry_scores[entry_id]["score"] += 1

    scored = list(entry_scores.values())
    scored.sort(key=lambda item: item["score"], reverse=True)
    evidence = [item["entry"] for item in scored[:max_results]]

    return {
        "evidence": evidence,
        "used": bool(evidence),
        "engine": "fallback_keyword"
    }


def retrieve_knowledge(query: str) -> Dict[str, object]:
    return retrieve_evidence(query)
