# output/phrase_builder.py — CCM v8
#
# Builds phrases compositionally from slots — no hardcoded strings.
#
# MAIN FLOW:
#   build_phrase()          → responds to identity questions
#   build_reactive_phrase() → reactive phrase based on quadrant + tension
#   build_contradiction_phrase() → negates logical contradictions
#
# FORMATS:
#   Each quadrant/tension defines a list of slots.
#   resolve_slot() resolves each slot from active_concepts + core + memory.
#   No complete phrase is stored anywhere.

from db.db_concepts import CONCEPTS

MENTAL_RESPOND_THRESHOLD = 90.0

# ── FORMATS ───────────────────────────────────────────────────────────────────
# Slot lists per (quadrant, tension).
# Slots disponibles: subject_internal, subject_external, focus, verb,
#                    property, value, negation, exclamation

FORMATS = {
    "present-emotional": {
        "low":      ["subject_internal", "verb", "focus"],
        "medium":   ["subject_internal", "verb", "focus"],
        "high":     ["verb", "focus"],
        "critical": ["exclamation"],
    },
    "present-rational": {
        "low":      ["subject_internal", "verb", "focus"],
        "medium":   ["subject_internal", "property", "verb", "focus"],
        "high":     ["property", "verb", "focus"],
        "critical": ["subject_internal", "property", "verb", "focus"],
    },
    "absent-emotional": {
        "low":      ["subject_internal", "emotion_state", "focus"],
        "medium":   ["subject_internal", "emotion_state", "focus"],
        "high":     ["emotion_state", "focus"],
        "critical": ["exclamation"],
    },
    "absent-rational": {
        "low":      ["subject_internal", "negation", "verb", "focus"],
        "medium":   ["negation", "focus"],
        "high":     ["negation"],
        "critical": [],   # no verbal — somatic takes control
    },
}

# ── SLOT RESOLVER ─────────────────────────────────────────────────────────────

def resolve_slot(slot, active_concepts, core_rules, focus=None, memory_value=None,
                 quadrant=None, valence=None, emotion=None):
    """Resolves a slot → word/string."""

    if slot == "subject_internal":
        return "I"

    if slot == "subject_external":
        return "you"

    if slot == "focus":
        if focus:
            # Use the concept key as display label — synonyms are for input resolution only
            return focus
        return ""

    if slot == "property":
        for name in active_concepts:
            c = CONCEPTS.get(name, {})
            if c.get("subtype") == "property":
                return name
        return ""  # no property in scene — skip this slot

    if slot == "verb_ser":
        return "am"

    if slot == "verb":
        # state/being verb based on quadrant
        if quadrant and "absent" in quadrant:
            return "feel"
        return "sense"

    if slot == "value":
        # identity value from core_rules
        for _, rule in (core_rules or []):
            if rule.get("type") == "identity":
                val = rule.get("value", {})
                return val.get("name", "")
        return memory_value or ""

    if slot == "action":
        # direct action — comes as memory_value (already resolved externally)
        return memory_value or ""

    if slot == "negation":
        return "not"

    if slot == "exclamation":
        if valence == "positive":
            return "Yes!"
        return "No!"

    if slot == "emotion_state":
        return emotion or "feel"

    return ""


# ── HELPERS ───────────────────────────────────────────────────────────────────

def can_respond(dist_mental: float) -> bool:
    return dist_mental < MENTAL_RESPOND_THRESHOLD

def is_opening(dist_mental: float) -> bool:
    return dist_mental < 20.0

def _get_focus(active_concepts: list) -> str | None:
    """Returns the concept with the highest semantic weight (non-language)."""
    content = [c for c in active_concepts
               if CONCEPTS.get(c, {}).get("type", "") != "language"]
    return content[0] if content else None

def _threat_active(core_rules: list) -> bool:
    return any(rule.get("effect") == "guard_identity"
               for _, rule in (core_rules or []))

def _get_identity_value(core_rules: list, memory_value: str = None) -> str:
    for _, rule in (core_rules or []):
        if rule.get("type") == "identity":
            return rule.get("value", {}).get("name", "")
    return memory_value or ""

def detect_pattern(active_concepts: list) -> dict:
    pattern = {
        "type":            None,
        "has_interrogant": False,
        "has_verb":        False,
        "has_property":    False,
        "has_subject_ext": False,
        "has_subject_int": False,
        "property_name":   None,
    }
    for name in active_concepts:
        c       = CONCEPTS.get(name, {})
        subtype = c.get("subtype", "")
        if c.get("type") != "language":
            continue
        if subtype == "question_word": pattern["has_interrogant"] = True
        elif subtype == "verb":        pattern["has_verb"] = True
        elif subtype == "property":
            pattern["has_property"]  = True
            pattern["property_name"] = name
        elif subtype == "external_subject": pattern["has_subject_ext"] = True
        elif subtype == "internal_subject": pattern["has_subject_int"] = True

    if pattern["has_interrogant"]:
        pattern["type"] = "question"
    elif pattern["has_verb"] or pattern["has_property"]:
        pattern["type"] = "statement"
    return pattern


# ── BUILD FROM FORMAT ─────────────────────────────────────────────────────────

def build_from_format(fmt, active_concepts, core_rules, focus=None,
                      memory_value=None, quadrant=None, valence=None, emotion=None):
    """
    Fills a list of slots and returns the composed phrase.
    Returns None if the format is empty or all slots are empty.
    """
    if not fmt:
        return None
    parts = []
    for slot in fmt:
        word = resolve_slot(slot, active_concepts, core_rules, focus=focus,
                            memory_value=memory_value, quadrant=quadrant,
                            valence=valence, emotion=emotion)
        if word:
            parts.append(word)
    if not parts:
        return None
    phrase = " ".join(parts)
    return phrase[0].upper() + phrase[1:]


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def build_phrase(active_concepts: list, core_rules: list,
                 dist_mental: float, memory_value: str = None) -> str | None:
    """
    Responds to identity questions if the host can respond.
    Uses FORMATS["present-rational"] with identity slots.
    """
    if not can_respond(dist_mental):
        return None

    pattern = detect_pattern(active_concepts)

    if pattern["type"] == "question":
        if _threat_active(core_rules):
            return "I won't tell you!"
        if (pattern["has_property"] and pattern["property_name"] in ("name", "identity")) \
                or pattern["has_subject_ext"] or pattern["has_interrogant"]:
            value = _get_identity_value(core_rules, memory_value)
            if value:
                fmt = ["subject_internal", "verb_ser", "value"] if dist_mental < 50 else ["value"]
                return build_from_format(fmt, active_concepts, core_rules,
                                         memory_value=value, quadrant="present-rational")

    if (pattern["type"] == "statement"
            and pattern["has_subject_ext"]
            and pattern["has_property"]
            and pattern["property_name"] in ("name", "identity")):
        if _threat_active(core_rules):
            return "I won't tell you!"
        value = _get_identity_value(core_rules, memory_value)
        if value:
            fmt = ["subject_internal", "verb_ser", "value"] if dist_mental < 50 else ["value"]
            return build_from_format(fmt, active_concepts, core_rules,
                                     memory_value=value, quadrant="present-rational")

    return None


def build_reactive_phrase(active_concepts: list, cfx: float, tension: str,
                           quadrant: str, dist_mental: float,
                           emotion: str = None) -> str | None:
    """
    Reactive phrase based on quadrant + tension.
    Selects the format from FORMATS and fills it with resolve_slot.
    """
    if not can_respond(dist_mental):
        return None

    from layers.processing_mode import get_processing_mode

    pm      = get_processing_mode(cfx, tension)
    focus   = _get_focus(active_concepts)
    valence = "positive" if "present" in quadrant else "negative"

    if pm["preverbal"]:
        return None

    fmt = FORMATS.get(quadrant, {}).get(tension)
    return build_from_format(fmt, active_concepts, core_rules=[], focus=focus,
                              quadrant=quadrant, valence=valence, emotion=emotion)


def build_contradiction_phrase(contradiction_info: dict, dist_mental: float) -> str | None:
    """
    Negates logical contradictions (e.g.: "fish don't fly").
    """
    if not contradiction_info.get("is_contradiction"):
        return None
    if dist_mental >= 90:
        return None

    subj = contradiction_info.get("subject_label", "that")
    act  = contradiction_info.get("action_label",  "do that")

    fmt = ["subject_external", "negation", "action", "focus"] if dist_mental < 50 else ["negation", "action", "focus"]
    return build_from_format(fmt, active_concepts=[], core_rules=[],
                              focus=subj, memory_value=act, quadrant=None)
