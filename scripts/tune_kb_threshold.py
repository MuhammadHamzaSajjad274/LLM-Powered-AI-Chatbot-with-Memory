#!/usr/bin/env python3
"""
Throwaway script to inspect raw KB retrieval distances and tune kb_distance_threshold.

Not part of the permanent test suite.
"""

import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.embeddings import Embedder
from core.kb_retriever import KBRetriever

QUERIES = [
    ("billing", "How much does the Pro plan cost per month?"),
    ("troubleshooting-sync", "I'm getting error FB-SYNC-102, how do I fix stale session sync?"),
    ("troubleshooting-login", "I forgot my password and can't log in to FlowBoard"),
    ("security", "Is FlowBoard GDPR compliant and where is data stored?"),
    ("integrations-slack", "How do I connect FlowBoard to Slack and use slash commands?"),
    ("integrations-github", "How do I link a GitHub pull request to a FlowBoard task?"),
    ("automations", "What triggers and actions are available in FlowBoard automations?"),
    ("team-management", "What is the difference between Admin and Owner roles?"),
    ("getting-started", "How do I invite teammates to my FlowBoard workspace?"),
    ("api-webhooks", "What is the API rate limit and how are webhooks signed?"),
]


def raw_top_k(kb: KBRetriever, query: str, top_k: int = 3):
    count = kb.collection.count()
    if count == 0:
        return []
    embedding = kb.embedder.embed_query(query)
    results = kb.collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )
    rows = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            rows.append(
                {
                    "distance": results["distances"][0][i],
                    "source_file": (results["metadatas"][0][i] or {}).get("source_file", "?"),
                    "preview": results["documents"][0][i][:100].replace("\n", " "),
                }
            )
    return rows


def main() -> None:
    embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    kb = KBRetriever(embedder=embedder)

    print("KB Threshold Tuning — Raw Distance Report")
    print("=" * 70)
    print(f"Collection count: {kb.get_collection_count()}")
    print(f"Current threshold (not applied here): {kb.kb_distance_threshold}")
    print()

    top1_distances = []

    for topic, query in QUERIES:
        print(f"[{topic}] {query}")
        rows = raw_top_k(kb, query, top_k=3)
        if not rows:
            print("  (no results)")
            print()
            continue
        top1_distances.append(rows[0]["distance"])
        for rank, row in enumerate(rows, 1):
            print(
                f"  #{rank} dist={row['distance']:.4f}  "
                f"file={row['source_file']}  preview={row['preview']}..."
            )
        print()

    if top1_distances:
        print("=" * 70)
        print("Top-1 distance summary (across all queries):")
        print(f"  min    : {min(top1_distances):.4f}")
        print(f"  max    : {max(top1_distances):.4f}")
        print(f"  median : {statistics.median(top1_distances):.4f}")
        print(f"  mean   : {statistics.mean(top1_distances):.4f}")
        print()
        for t in [0.40, 0.45, 0.50, 0.55, 0.60]:
            kept = sum(1 for d in top1_distances if d < t)
            print(f"  threshold {t:.2f} -> keeps top-1 for {kept}/{len(top1_distances)} queries")


if __name__ == "__main__":
    main()
