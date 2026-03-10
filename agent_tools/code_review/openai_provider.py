"""OpenAI provider for code review."""

import os

from agent_tools.code_review.models import ReviewCost

EMPTY = {"summary": "No review generated.", "findings": []}

# Approximate $/token pricing (input, output)
OPENAI_PRICING = {
    "gpt-5.1-codex-mini": (0.25 / 1e6, 2.00 / 1e6),
    "codex-mini-latest": (0.25 / 1e6, 2.00 / 1e6),
    "gpt-5.3-codex": (1.75 / 1e6, 14.00 / 1e6),
    "gpt-5.1-codex": (1.25 / 1e6, 10.00 / 1e6),
    "gpt-5-codex": (1.25 / 1e6, 10.00 / 1e6),
    "gpt-5.4": (2.50 / 1e6, 15.00 / 1e6),
    "gpt-5-mini": (0.25 / 1e6, 2.00 / 1e6),
    "gpt-5-nano": (0.10 / 1e6, 0.40 / 1e6),
    "gpt-4.1": (2.00 / 1e6, 8.00 / 1e6),
    "gpt-4o": (2.50 / 1e6, 10.00 / 1e6),
    "gpt-4o-mini": (0.15 / 1e6, 0.60 / 1e6),
}
DEFAULT_MODEL = "gpt-5.1-codex-mini"

# Models that require the Responses API
RESPONSES_MODELS = {
    "gpt-5.1-codex-mini", "codex-mini-latest",
    "gpt-5.3-codex", "gpt-5.1-codex", "gpt-5-codex",
}


def _uses_responses_api(model):
    """Check if a model requires the Responses API.

    Args:
        model (str): The OpenAI model name.

    Returns:
        bool: True if the model needs Responses API.
    """
    return model in RESPONSES_MODELS or "codex" in model


def _estimate_cost(usage, model):
    """Estimate cost from OpenAI usage data.

    Args:
        usage: The response.usage object from OpenAI.
        model (str): Model name for price lookup.

    Returns:
        ReviewCost: Estimated cost and token counts.
    """
    in_tok = (
        getattr(usage, "prompt_tokens", 0)
        or getattr(usage, "input_tokens", 0)
        or 0
    )
    out_tok = (
        getattr(usage, "completion_tokens", 0)
        or getattr(usage, "output_tokens", 0)
        or 0
    )
    in_price, out_price = OPENAI_PRICING.get(
        model, (2.50 / 1e6, 10.00 / 1e6),
    )
    cost = in_tok * in_price + out_tok * out_price
    return ReviewCost(
        input_tokens=in_tok,
        output_tokens=out_tok,
        cost_usd=cost,
        provider="openai",
        model=model,
    )


def _call_chat_completions(client, model, prompt):
    """Call the Chat Completions API.

    Args:
        client: OpenAI client instance.
        model (str): Model name.
        prompt (str): The review prompt.

    Returns:
        tuple: (raw_text str, usage object).
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a senior code reviewer. "
                "Respond with JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw = response.choices[0].message.content
    return raw, response.usage


def _call_responses(client, model, prompt):
    """Call the Responses API for codex models.

    Args:
        client: OpenAI client instance.
        model (str): Model name.
        prompt (str): The review prompt.

    Returns:
        tuple: (raw_text str, usage object).
    """
    kwargs = {
        "model": model,
        "instructions": "You are a senior code reviewer. "
        "Respond with JSON only.",
        "input": prompt,
    }
    if "codex" not in model:
        kwargs["temperature"] = 0
    response = client.responses.create(**kwargs)
    raw = response.output_text
    return raw, response.usage


def review_openai(prompt, model=DEFAULT_MODEL, extract_json=None):
    """Run review via OpenAI API.

    Auto-selects Chat Completions or Responses API
    based on the model. Codex models use Responses.

    Args:
        prompt (str): The full review prompt.
        model (str): OpenAI model name to use.
        extract_json (callable): Function to parse
            JSON from raw text.

    Returns:
        tuple: (review_data dict, ReviewCost).

    Raises:
        ImportError: If the openai package is not
            installed.
        openai.APIError: If the API call fails.
    """
    empty_cost = ReviewCost(provider="openai", model=model)
    try:
        from openai import OpenAI
    except ImportError:
        print("  Error: pip install openai")
        return EMPTY, empty_cost

    if not os.environ.get("OPENAI_API_KEY"):
        print("  Error: set OPENAI_API_KEY")
        return EMPTY, empty_cost

    use_responses = _uses_responses_api(model)
    api_name = "responses" if use_responses else "chat"
    client = OpenAI()
    print(f"  OpenAI model: {model} (api: {api_name})")
    print(f"  Prompt length: {len(prompt)} chars")

    if use_responses:
        raw, usage = _call_responses(client, model, prompt)
    else:
        raw, usage = _call_chat_completions(
            client, model, prompt,
        )
    print(f"  OpenAI response: {raw[:500]}")

    cost = _estimate_cost(usage, model)
    data = extract_json(raw) if extract_json else EMPTY
    return data, cost
