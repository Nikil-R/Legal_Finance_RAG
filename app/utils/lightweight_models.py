"""
Lightweight local model fallbacks used when transformer models are unavailable.
"""

from __future__ import annotations

import hashlib
import re
from typing import Iterable

import numpy as np

VECTOR_DIM = 384
TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall((text or "").lower())


def _hashed_embedding(text: str) -> np.ndarray:
    vec = np.zeros(VECTOR_DIM, dtype=np.float32)
    tokens = _tokenize(text)
    if not tokens:
        return vec

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], byteorder="big") % VECTOR_DIM
        vec[idx] += 1.0

    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec /= norm
    return vec


class FallbackSentenceEncoder:
    """Deterministic, dependency-free embedding fallback."""

    def __init__(self, model_name: str) -> None:
        self.model_name = f"fallback::{model_name}"

    def encode(
        self,
        texts: str | Iterable[str],
        *,
        normalize_embeddings: bool = False,
        convert_to_numpy: bool = False,
        **_: object,
    ):
        single = isinstance(texts, str)
        corpus = [texts] if single else list(texts)

        if corpus:
            matrix = np.vstack([_hashed_embedding(text) for text in corpus])
        else:
            matrix = np.empty((0, VECTOR_DIM), dtype=np.float32)

        if normalize_embeddings and len(matrix) > 0:
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1
            matrix = matrix / norms

        if single:
            return matrix[0]
        if convert_to_numpy:
            return matrix
        return matrix.tolist()


class FallbackCrossEncoder:
    """Simple lexical-overlap scorer fallback."""

    def __init__(self, model_name: str) -> None:
        self.model_name = f"fallback::{model_name}"

    def predict(self, pairs: Iterable[tuple[str, str]]) -> np.ndarray:
        scores: list[float] = []
        for query, passage in pairs:
            q_tokens = set(_tokenize(query))
            p_tokens = set(_tokenize(passage))
            if not q_tokens:
                scores.append(0.0)
                continue
            overlap = len(q_tokens & p_tokens)
            scores.append(float(overlap) / float(len(q_tokens)))
        return np.array(scores, dtype=np.float32)


def load_sentence_encoder(model_name: str, *, device: str = "cpu", logger=None):
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name, device=device)
    except Exception as exc:  # pragma: no cover - depends on host/network state
        if logger is not None:
            logger.warning(
                "Falling back to lightweight sentence encoder for '%s': %s",
                model_name,
                exc,
            )
        return FallbackSentenceEncoder(model_name)


def load_cross_encoder(model_name: str, *, device: str = "cpu", logger=None):
    try:
        from sentence_transformers import CrossEncoder

        return CrossEncoder(model_name, device=device)
    except Exception as exc:  # pragma: no cover - depends on host/network state
        if logger is not None:
            logger.warning(
                "Falling back to lightweight cross encoder for '%s': %s",
                model_name,
                exc,
            )
        return FallbackCrossEncoder(model_name)

