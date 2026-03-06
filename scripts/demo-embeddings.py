#!/usr/bin/env python3
"""
Demo: get embeddings from a locally‑hosted Qwen3 model
"""

import json
import sys
from pathlib import Path
from typing import List

import numpy as np
import requests


# ------------------- configuration -------------------
API_URL = "http://localhost:8688/v1/embeddings"
# Qwen3 model name – replace with the exact name the server expects
MODEL_NAME = "llamacpp-Qwen3-Embedding-4B"        # e.g. "qwen3-embedding" or "text-embedding-3-large"
# If the server requires an auth header, set it here (or leave empty)
API_KEY = "sk-empty"                         # optional

HEADERS = {
    "Content-Type": "application/json",
    # Some self‑hosted servers still expect an Authorization header.
    # Omit if not needed.
    **({"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}),
}
# -----------------------------------------------------


def get_embeddings(texts):
    """Send a batch of texts to the /embeddings endpoint and return the vectors."""
    payload = {
        "model": MODEL_NAME,
        "input": texts,          # can be a str or a list of str
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[error] request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    # The OpenAI schema returns {"data": [{"embedding": [...], "index": 0, ...}, ...]}
    embeddings = [item["embedding"] for item in data.get("data", [])]
    return embeddings


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Return cosine similarity between two 1‑D arrays."""
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def pairwise_similarities(vectors: List[List[float]]) -> List[List[float]]:
    """Return NxN matrix of cosine similarities for the vectors."""
    arr = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1)
    # Avoid division by zero for degenerate vectors
    norms[norms == 0] = 1e-10
    dot = arr @ arr.T
    sim_matrix = dot / np.outer(norms, norms)
    return sim_matrix.tolist()


def main() -> None:
    if len(sys.argv) > 1:
        # Treat all positional args as the sentences
        sentences = sys.argv[1:]
    else:
        # Interactive mode – read until EOF (Ctrl‑D)
        print("Enter sentences, one per line. Send EOF (Ctrl‑D) when done.")
        sentences = sys.stdin.read().splitlines()

    if not sentences:
        print("[error] No sentences provided.")
        sys.exit(1)

    print("\nRequesting embeddings …")
    vectors = get_embeddings(sentences)

    # Print embeddings (dim + first 5 entries)
    for i, (txt, vec) in enumerate(zip(sentences, vectors)):
        print(f"\n[{i}]  \"{txt}\"")
        print(f"    dim: {len(vec)}")
        print(f"    vec[:5]: {vec[:5]}")

    # Compute and show cosine similarity matrix
    sim_mat = pairwise_similarities(vectors)
    print("\nCosine similarity matrix:")
    header = [f"[{i}]" for i in range(len(sentences))]
    print("\t".join(header))
    for i, row in enumerate(sim_mat):
        print(f"[{i}]\t" + "\t".join(f"{val:.4f}" for val in row))

    # Optional: save to JSON
    out_path = Path("embeddings_demo_output.json")
    out_path.write_text(
        json.dumps(
            {"texts": sentences, "embeddings": vectors, "similarity": sim_mat},
            indent=2,
        )
    )
    print(f"\nSaved full result to {out_path}")


if __name__ == "__main__":
    main()
