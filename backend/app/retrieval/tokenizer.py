from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{1,}")
STOP_WORDS = {
    "about", "after", "against", "all", "and", "are", "but", "for", "from", "has",
    "have", "into", "its", "not", "only", "our", "that", "the", "their", "this",
    "through", "use", "using", "with", "within", "you", "your", "must", "should",
}


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text) if token.lower() not in STOP_WORDS]


def term_frequencies(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def inverse_document_frequency(documents: Iterable[str]) -> dict[str, float]:
    docs = [set(tokenize(document)) for document in documents]
    total = max(len(docs), 1)
    counts: Counter[str] = Counter()
    for document in docs:
        counts.update(document)
    return {term: math.log((total + 1) / (count + 1)) + 1 for term, count in counts.items()}
