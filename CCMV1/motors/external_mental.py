# motors/external_mental.py — CCM v5
#
# engine external mental
# Delegates heavy lifting to pre_input — categorization, focus, multiplier.

from db.db_concepts import resolve_concept
from core.pre_input  import pre_input_mental

STOPWORDS = {"a", "an", "the", "in", "on", "at", "is", "are", "was", "i", "and", "or", "of"}


def process(tokens: list, extra_concepts: list = None, memory=None) -> dict | None:
    concept_names = _resolve_tokens(tokens)
    if extra_concepts:
        for c in extra_concepts:
            if c not in concept_names:
                concept_names.append(c)
    if not concept_names:
        return None
    return pre_input_mental(concept_names, memory=memory)


def resolve_text(text: str) -> list:
    tokens = [t for t in text.lower().split() if t not in STOPWORDS]
    return _resolve_tokens(tokens)


def _resolve_tokens(tokens: list) -> list:
    names = []
    for token in tokens:
        name = resolve_concept(token)
        if name and name not in names:
            names.append(name)
    return names
