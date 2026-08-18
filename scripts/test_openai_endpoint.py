#!/usr/bin/env python3
"""
Send review texts from Firebase to POST /analyze-openai and print usage summary.

Usage:
  1. Start the Flask app: python app.py
  2. Set OPENAI_API_KEY in .env
  3. Run: python scripts/test_openai_endpoint.py

Optional env vars:
  FLASK_HOST (default 127.0.0.1)
  FLASK_PORT (default 5000)
  OPENAI_TEST_REVIEW_COUNT (default 20, min 15)
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.firebase_service import get_review_texts, is_firebase_configured  # noqa: E402


def _api_base_url():
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = os.getenv("FLASK_PORT", "5000")
    return f"http://{host}:{port}"


def _target_review_count():
    configured = int(os.getenv("OPENAI_TEST_REVIEW_COUNT", "20"))
    return max(15, configured)


def main():
    if not is_firebase_configured():
        print("Error: Firebase is not configured. Set FIREBASE_CREDENTIALS_PATH in .env.")
        return 1

    review_count = _target_review_count()
    reviews = get_review_texts(limit=review_count)
    if not reviews:
        print(
            "Error: No review texts found in the configured Firebase collection "
            f"({os.getenv('FIREBASE_COLLECTION', 'reviews')})."
        )
        return 1

    if len(reviews) < 15:
        print(
            f"Warning: only {len(reviews)} review texts found in Firebase; "
            "continuing with available reviews."
        )

    endpoint = f"{_api_base_url()}/analyze-openai"
    print(f"Sending {len(reviews)} reviews to {endpoint}")

    totals = {
        "processed": 0,
        "failed": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "latency_seconds": 0.0,
    }

    for index, text in enumerate(reviews, start=1):
        preview = text.replace("\n", " ")[:80]
        print(f"[{index}/{len(reviews)}] {preview!r}")

        try:
            response = requests.post(
                endpoint,
                json={"text": text},
                timeout=float(os.getenv("OPENAI_REQUEST_TIMEOUT", "60")),
            )
        except requests.RequestException as exc:
            totals["failed"] += 1
            print(f"  request failed: {exc}")
            continue

        try:
            payload = response.json()
        except ValueError:
            totals["failed"] += 1
            print(f"  non-JSON response ({response.status_code}): {response.text[:200]}")
            continue

        if response.status_code != 200:
            totals["failed"] += 1
            print(f"  HTTP {response.status_code}: {payload.get('error', payload)}")
            continue

        usage = payload.get("usage", {})
        totals["processed"] += 1
        totals["input_tokens"] += int(usage.get("input_tokens", 0))
        totals["output_tokens"] += int(usage.get("output_tokens", 0))
        totals["cost_usd"] += float(usage.get("cost_usd", 0.0))
        totals["latency_seconds"] += float(usage.get("latency_seconds", 0.0))

        print(
            "  "
            f"sentiment={payload.get('sentiment')} "
            f"input_tokens={usage.get('input_tokens')} "
            f"output_tokens={usage.get('output_tokens')} "
            f"cost_usd={usage.get('cost_usd')} "
            f"latency_seconds={usage.get('latency_seconds')}"
        )

    average_latency = (
        totals["latency_seconds"] / totals["processed"] if totals["processed"] else 0.0
    )

    print("\nSummary")
    print(f"  total reviews processed: {totals['processed']}")
    print(f"  total reviews failed:    {totals['failed']}")
    print(f"  total input tokens:      {totals['input_tokens']}")
    print(f"  total output tokens:     {totals['output_tokens']}")
    print(f"  total cost (USD):        {totals['cost_usd']:.8f}")
    print(f"  average latency (sec):   {average_latency:.4f}")

    return 0 if totals["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
