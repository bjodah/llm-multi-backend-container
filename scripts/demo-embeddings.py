#!/usr/bin/env python3
"""
Demo: get embeddings from a locally‑hosted Qwen3 model
"""

import json
import sys
from pathlib import Path

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


def main():
    # Example inputs – feel free to replace or read from a file/CLI
    examples = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial intelligence is transforming many industries."
    ]

    print("Requesting embeddings …")
    vectors = get_embeddings(examples)

    for i, (txt, vec) in enumerate(zip(examples, vectors)):
        print(f"\n[{i}]  \"{txt}\"")
        print(f"    dim: {len(vec)}")
        # show first 5 numbers for brevity
        print(f"    vec[:5]: {vec[:5]}")

    # Optional: save to JSON for later use
    out_path = Path("embeddings_demo_output.json")
    out_path.write_text(json.dumps({"texts": examples, "embeddings": vectors}, indent=2))
    print(f"\nSaved full result to {out_path}")


if __name__ == "__main__":
    main()
