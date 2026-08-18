import json
import time

from openai import APIConnectionError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError

from app.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_REQUEST_TIMEOUT,
    GPT_35_TURBO_INPUT_USD_PER_TOKEN,
    GPT_35_TURBO_OUTPUT_USD_PER_TOKEN,
)


class OpenAIAnalyzerError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def _calculate_cost_usd(input_tokens, output_tokens):
    input_cost = input_tokens * GPT_35_TURBO_INPUT_USD_PER_TOKEN
    output_cost = output_tokens * GPT_35_TURBO_OUTPUT_USD_PER_TOKEN
    return input_cost + output_cost


def analyze_sentiment_openai(text):
    """
    Classify review sentiment via OpenAI chat completions.

    Returns a dict with sentiment, reason, token usage, cost, and latency.
    """
    if not OPENAI_API_KEY:
        raise OpenAIAnalyzerError("OPENAI_API_KEY is not configured", status_code=503)

    client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_REQUEST_TIMEOUT)

    messages = [
        {
            "role": "system",
            "content": (
                "You classify product review sentiment. "
                'Respond with JSON only: {"sentiment": "positive"|"negative"|"neutral", '
                '"reason": "<one sentence explanation>"}.'
            ),
        },
        {"role": "user", "content": text},
    ]

    started_at = time.time()
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )
    except RateLimitError as exc:
        raise OpenAIAnalyzerError("OpenAI rate limit exceeded", status_code=429) from exc
    except APITimeoutError as exc:
        raise OpenAIAnalyzerError("OpenAI request timed out", status_code=504) from exc
    except AuthenticationError as exc:
        raise OpenAIAnalyzerError("OpenAI authentication failed; check OPENAI_API_KEY", status_code=401) from exc
    except APIConnectionError as exc:
        raise OpenAIAnalyzerError("Could not connect to OpenAI API", status_code=502) from exc
    except Exception as exc:
        raise OpenAIAnalyzerError(f"OpenAI API request failed: {exc}", status_code=502) from exc

    latency_seconds = time.time() - started_at

    if not response.choices:
        raise OpenAIAnalyzerError("OpenAI returned no completion choices", status_code=502)

    content = response.choices[0].message.content
    if not content:
        raise OpenAIAnalyzerError("OpenAI returned an empty response", status_code=502)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OpenAIAnalyzerError("OpenAI returned malformed JSON", status_code=502) from exc

    sentiment = str(parsed.get("sentiment", "")).lower().strip()
    reason = str(parsed.get("reason", "")).strip()

    if sentiment not in ("positive", "negative", "neutral"):
        raise OpenAIAnalyzerError(
            f"OpenAI returned invalid sentiment value: {sentiment or '<missing>'}",
            status_code=502,
        )
    if not reason:
        raise OpenAIAnalyzerError("OpenAI response missing reason field", status_code=502)

    usage = response.usage
    input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)

    return {
        "sentiment": sentiment,
        "reason": reason,
        "model": OPENAI_MODEL,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": _calculate_cost_usd(input_tokens, output_tokens),
        "latency_seconds": latency_seconds,
    }
