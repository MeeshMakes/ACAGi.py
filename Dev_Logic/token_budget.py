from __future__ import annotations

import math
import re
from functools import lru_cache
from typing import Dict

try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    tiktoken = None  # type: ignore

# Conservative defaults based on common context lengths.
_MODEL_TOKEN_LIMITS: Dict[str, int] = {
    "qwen3": 32768,
    "qwen2": 32768,
    "qwen": 32768,
    "llama3": 8192,
    "llama-3": 8192,
    "llama2": 4096,
    "llama-2": 4096,
    "mistral": 8192,
    "mixtral": 8192,
    "phi3": 4096,
    "phi-3": 4096,
    "phi2": 4096,
    "codellama": 16384,
    "deepseek": 16384,
    "gpt-4o": 128000,
    "gpt-4": 8192,
    "gpt-3.5": 4096,
}

_DEFAULT_MAX_TOKENS = 8192
_WORD_RE = re.compile(r"\S+")


@lru_cache(maxsize=32)
def _encoding_for_model(model: str | None):  # pragma: no cover - simple cache
    if not tiktoken:
        return None
    name = (model or "").strip() or "cl100k_base"
    try:
        return tiktoken.encoding_for_model(name)
    except Exception:
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None


def get_model_token_limit(model: str | None) -> int:
    """Return the maximum prompt tokens supported by ``model``.

    The lookup is intentionally fuzzy — if a known pattern appears within the
    model name we use the associated limit. Unknown models fall back to a
    conservative default so callers always receive a positive integer.
    """

    if not model:
        return _DEFAULT_MAX_TOKENS
    key = model.lower()
    for pattern, limit in _MODEL_TOKEN_LIMITS.items():
        if pattern in key:
            return limit
    return _DEFAULT_MAX_TOKENS


def prompt_token_budget(model: str | None, headroom_pct: int) -> int:
    """Compute the usable prompt budget given a headroom percentage."""

    limit = get_model_token_limit(model)
    pct = max(1, min(int(headroom_pct or 0), 100))
    return int(limit * (pct / 100.0))


def count_tokens(text: str, model: str | None = None) -> int:
    """Count tokens for ``text`` using an optional tokenizer fallback."""

    if not text:
        return 0
    encoding = _encoding_for_model(model)
    if encoding:
        try:
            return len(encoding.encode(text))
        except Exception:
            pass
    tokens = _WORD_RE.findall(text)
    if tokens:
        return len(tokens)
    # Fallback heuristic when whitespace tokenisation fails (e.g. CJK text).
    return max(1, math.ceil(len(text) / 4))
