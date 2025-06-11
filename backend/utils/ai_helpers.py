"""AI helper utilities for RecallGuard
====================================

A thin, central wrapper around OpenAI (or compatible) endpoints that
provides:

*   Robust synchronous **and** asynchronous helpers for chat‑based
    completions and embeddings.
*   Automatic retry/back‑off for transient API errors / rate limits.
*   Environment‑driven configuration (model names, base URL, API key)
    via :pyfunc:`utils.config.get_settings`.
*   Simple text‑chunking + multi‑pass summarisation that can handle very
    long inputs by recursively summarising intermediate chunks.

Import this module whenever you need to call an LLM or create embeddings
inside the backend.  Keeping all OpenAI plumbing in one place makes it
trivial to swap providers (e.g. Anthropic, Azure OpenAI) or add
instrumentation later.
"""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Sequence

import backoff
import openai

from utils.config import get_settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
settings = get_settings()
openai.api_key = settings.openai_api_key
openai.base_url = settings.openai_base_url  # Optional –– falls back to OpenAI

# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------

def _is_transient(exc: Exception) -> bool:  # pragma: no cover
    """Return *True* if *exc* is worth retrying (rate‑limit, network, 5xx)."""
    transient_types = (
        openai.error.RateLimitError,
        openai.error.APIError,
        openai.error.Timeout,
        openai.error.APIConnectionError,
    )
    return isinstance(exc, transient_types)


def _with_retry():  # pragma: no cover – declarative helper
    """backoff decorator for transient OpenAI errors."""
    return backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=5,
        jitter=backoff.full_jitter,
        giveup=lambda e: not _is_transient(e),
        logger=logger,
    )


# ---------------------------------------------------------------------------
# Model helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=8)
def _chat_model(default: str | None = None) -> str:  # noqa: D401
    "Return the chat model – cached because we call this often."  # noqa: D401
    return default or settings.openai_chat_model


@lru_cache(maxsize=8)
def _embed_model(default: str | None = None) -> str:  # noqa: D401
    "Return the embedding model – cached because we call this often."  # noqa: D401
    return default or settings.openai_embedding_model


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

@_with_retry()
def chat_completion(
    messages: Sequence[Dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> str:
    """Blocking wrapper around *chat/completions* returning the *content* str."""
    response = openai.ChatCompletion.create(
        model=_chat_model(model),
        messages=list(messages),
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
    return response.choices[0].message["content"].strip()


@_with_retry()
def embed_text(texts: str | Sequence[str], *, model: str | None = None) -> List[List[float]]:
    """Return embeddings for one or many documents."""
    if isinstance(texts, str):
        texts = [texts]
    resp = openai.Embedding.create(input=list(texts), model=_embed_model(model))
    return [item["embedding"] for item in resp["data"]]


async def async_chat_completion(
    messages: Sequence[Dict[str, str]],
    **kwargs: Any,
) -> str:
    """Async wrapper using an executor so we don't block the event‑loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: chat_completion(messages, **kwargs))


# ---------------------------------------------------------------------------
# Convenience utilities
# ---------------------------------------------------------------------------

def chunk_text(text: str, *, max_tokens: int = 800, overlap: int = 120) -> List[str]:
    """Split *text* into rough token‑sized chunks with overlap for context."""
    words = text.split()
    approx_tokens_per_word = 1  # heuristic – adjust if you switch tokenizer
    chunk_size = max_tokens // approx_tokens_per_word
    step = chunk_size - overlap // approx_tokens_per_word

    chunks: List[str] = []
    for i in range(0, len(words), max(step, 1)):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def summarise(text: str, *, prompt: str | None = None) -> str:
    """Recursive map‑reduce summariser that handles arbitrarily long docs."""
    if len(text.split()) < 700:  # heuristic – single pass is fine
        messages = [
            {"role": "system", "content": prompt or "You are a concise technical writer."},
            {"role": "user", "content": f"Please summarise the following text as bullet‑points: \n\n{text}"},
        ]
        return chat_completion(messages, temperature=0)

    partials = [summarise(chunk, prompt=prompt) for chunk in chunk_text(text)]
    combined = "\n".join(partials)
    return summarise(combined, prompt="Combine the following partial summaries into a single cohesive summary.")


__all__ = [
    "chat_completion",
    "async_chat_completion",
    "embed_text",
    "summarise",
    "chunk_text",
]
