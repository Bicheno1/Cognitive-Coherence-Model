# motors/core_identity.py — CCM v5
#
# CORE IDENTITY — permanent identity of the host
#
# RECEIVES: input vector (somatic or mental) + active concepts
# DOES:     consults CORE_RULES — amplifies or contains the vector
# OUTPUTS:  modified vector + active rules
#
# NEVER changes per tick. Only changes if the host experiences a nuclear event.
# Permanent personality layer: fears, beliefs, traumas, values.

from db.db_concepts import resolve_concept

CORE_RULES = {
    "host_identity": {
        "type":     "identity",
        "concepts": ["name", "identity", "self", "which", "who", "tu", "julia"],
        "effect":   "none",
        "factor":   1.0,
        "value":    {"name": "Julia", "age": 28, "height": "163cm"},
        "note":     "Base identity of the host — replace with target agent",
    },
    "fear_of_ghosts": {
        "type":     "fear",
        "concepts": ["ghost", "shadow", "supernatural", "spirit", "phantom"],
        "effect":   "amplify",
        "factor":   2.0,
        "note":     "Saw a ghost as a child — maximum terror",
    },
    "darkness_danger": {
        "type":     "fear",
        "concepts": ["dark", "darkness", "night", "dark_sp"],
        "effect":   "amplify",
        "factor":   1.6,
        "note":     "Darkness triggers childhood memory",
    },
    "light_safety": {
        "type":     "relief",
        "concepts": ["light", "safe", "calm"],   # removed "person" — aggressive person does not provide relief
        "effect":   "contain",
        "factor":   0.4,
        "note":     "Light and calm reduce terror",
    },
    "threat_to_identity": {
        "type":     "defense",
        "concepts": ["aggressive", "threat", "danger"],
        "effect":   "guard_identity",
        "factor":   1.0,
        "note":     "Direct threat — protects identity, does not reveal name",
    },
}


def consult(concept_names: list) -> list:
    """Returns list of (rule_name, rule) for active concepts."""
    canonical = set()
    for c in concept_names:
        name = resolve_concept(c) or c
        canonical.add(name)
    active = []
    for rule_name, rule in CORE_RULES.items():
        if canonical & set(rule["concepts"]):
            active.append((rule_name, rule))
    return active


def apply(vector: dict, keys: list, active_rules: list) -> dict:
    """
    Receives vector + list of active rules.
    Returns the modified vector by amplification/containment factor.
    """
    if not active_rules:
        return vector
    from db.db_somatic import SOMATIC_MAX
    from db.db_mental  import MENTAL_MAX
    cap   = SOMATIC_MAX if any(k in keys for k in ("V", "I", "Lv", "Gv")) else MENTAL_MAX
    result = dict(vector)
    for rule_name, rule in active_rules:
        factor = rule["factor"]
        effect = rule["effect"]
        if effect == "amplify":
            for k in keys:
                if k in result and isinstance(result[k], float):
                    result[k] = min(result[k] * factor, float(cap))
        elif effect == "contain":
            for k in keys:
                if k in result and isinstance(result[k], float):
                    result[k] = result[k] * factor
    result["_core_rules"] = [r[0] for r in active_rules]
    return result


def apply_to_output(output: dict, active_rules: list, concept_names: list = None) -> dict:
    """Modifies the final output (tension, speed) based on active rules."""
    if not active_rules:
        return output

    concept_set = set(concept_names or [])

    for rule_name, rule in active_rules:
        effect = rule["effect"]
        factor = rule["factor"]

        if effect == "guard_identity":
            # threat directa + pregunta de identity → rechazo firme
            if concept_set & {"name", "identity", "who", "tu"}:
                output["verbal"]       = "i won't tell you!"
                output["core_applied"] = rule_name
            tension_map = {"low":"medium","medium":"high","high":"critical","critical":"critical"}
            output["movement"]["tension"]   = tension_map.get(
                output["movement"]["tension"], "high")
            output["movement"]["speed"] *= 1.2

        elif effect == "contain":
            tension_map = {"critical":"high","high":"medium","medium":"low","low":"low"}
            output["movement"]["tension"]   = tension_map.get(
                output["movement"]["tension"], "low")
            output["movement"]["speed"] *= 0.5
            output["core_applied"] = rule_name

        elif effect == "amplify":
            tension_map = {"low":"medium","medium":"high","high":"critical","critical":"critical"}
            output["movement"]["tension"]   = tension_map.get(
                output["movement"]["tension"], "high")
            output["movement"]["speed"] *= factor
            output["core_applied"] = rule_name

    return output
