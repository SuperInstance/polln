#!/usr/bin/env python3
"""
Vectorize all SuperInstance papers into Qdrant for semantic search.
Enables cross-paper synergy and research discovery.
"""

import os
import glob
import hashlib
import json
import requests
from pathlib import Path

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "superinstance_papers"
PAPERS_DIR = Path(__file__).parent.parent / "papers"

def get_paper_files():
    """Find all markdown files in papers directory."""
    papers = []
    for md_file in glob.glob(str(PAPERS_DIR / "**" / "*.md"), recursive=True):
        papers.append(Path(md_file))
    return sorted(papers)

def generate_embedding_placeholder(text: str) -> list:
    """
    Generate placeholder embedding (1536 dimensions).
    In production, use OpenAI embeddings or local model.
    """
    # Create deterministic pseudo-embedding based on content hash
    # This is a placeholder - replace with actual embeddings
    import numpy as np
    np.random.seed(hash(text) % (2**32))
    return np.random.randn(1536).tolist()

def extract_paper_metadata(filepath: Path) -> dict:
    """Extract metadata from paper file."""
    content = filepath.read_text(encoding='utf-8')

    # Extract title from first heading
    lines = content.split('\n')
    title = filepath.stem
    for line in lines[:20]:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Get paper number from path
    paper_num = filepath.parent.name.split('-')[0] if '-' in filepath.parent.name else "XX"

    return {
        "title": title,
        "paper_number": paper_num,
        "filename": filepath.name,
        "path": str(filepath.relative_to(PAPERS_DIR)),
        "word_count": len(content.split()),
        "content_preview": content[:500]
    }

def vectorize_papers():
    """Vectorize all papers and insert into Qdrant."""
    papers = get_paper_files()
    print(f"Found {len(papers)} paper files")

    points = []
    for i, paper_path in enumerate(papers):
        try:
            content = paper_path.read_text(encoding='utf-8')
            metadata = extract_paper_metadata(paper_path)

            # Generate embedding
            embedding = generate_embedding_placeholder(content)

            # Create point
            point = {
                "id": str(i + 1),
                "vector": embedding,
                "payload": {
                    **metadata,
                    "full_content": content[:10000],  # Truncate for storage
                    "indexed_at": datetime.now().isoformat() if 'datetime' in dir() else ""
                }
            }
            points.append(point)

            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(papers)} papers...")

        except Exception as e:
            print(f"Error processing {paper_path}: {e}")

    # Batch insert into Qdrant
    print(f"Inserting {len(points)} points into Qdrant...")

    response = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points",
        headers={"Content-Type": "application/json"},
        json={
            "points": points,
            "wait": True
        }
    )

    if response.status_code == 200:
        print(f"Successfully vectorized {len(points)} papers!")
    else:
        print(f"Error: {response.text}")

    return points

def search_papers(query: str, limit: int = 5):
    """Search for papers semantically."""
    # Generate embedding for query
    query_embedding = generate_embedding_placeholder(query)

    response = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/search",
        headers={"Content-Type": "application/json"},
        json={
            "vector": query_embedding,
            "limit": limit,
            "with_payload": True
        }
    )

    return response.json()

if __name__ == "__main__":
    print("=" * 60)
    print("SuperInstance Papers Vectorization")
    print("=" * 60)

    # Vectorize all papers
    points = vectorize_papers()

    # Test search
    print("\n" + "=" * 60)
    print("Testing semantic search...")
    results = search_papers("self-play mechanisms for distributed systems")
    print(f"Found {len(results.get('result', []))} results")
