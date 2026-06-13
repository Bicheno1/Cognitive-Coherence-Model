# core/pre_input.py — CCM v5
#
# Pre-input — categorizador y amplificador
#
# FLUJO:
#   step 1 — Identificar focus y calcular multiplier
#     - focus = concept de mayor prioridad (illogical > subject > action > status > environment > object)
#     - multiplier = number of related items of the focus that appear in the related
#       of other concepts in the scene + 1
#     - Ejemplo: ghost tiene [danger, fear, defenseless]
#                dark  tiene [fear, danger, uncertainty]
#                fear coincide → +1, danger coincide → +1
#                ghost = x3 (2 matches + 1)
#
#   step 2 — Buscar focus en memory
#     - If the focus appears in short/medium/long term of the memory system
#     - The graph of the event is taken → median point (start, peak, end)
#     - That vector enters via the interference formula on top of step 1 result
#
#   result → goes to the external motors (somatic and mental)

from collections import Counter

PRIORITY = ["illogical", "subject", "action", "status", "environment", "object"]
STATUS_SUBTYPE_PRIORITY = ["threat", "emotional", "physical", "social", "safety", "condition"]

VISUAL_SENSE   = "sight"
RECEPTOR_SENSES = {"touch", "hearing", "smell", "taste"}


# ── step 1 — focus Y multiplier ─────────────────────────────────────────────

def _get_focus(concept_names, concepts_db):
    best_name, best_score = None, (999, 999)
    for name in concept_names:
        c = concepts_db.get(name)
        if not c:
            continue
        ctype   = c.get("type", "object")
        subtype = c.get("subtype", "")
        type_score = PRIORITY.index(ctype) if ctype in PRIORITY else 999
        sub_score  = STATUS_SUBTYPE_PRIORITY.index(subtype) if (ctype == "status" and subtype in STATUS_SUBTYPE_PRIORITY) else 999
        if (type_score, sub_score) < best_score:
            best_score = (type_score, sub_score)
            best_name  = name
    return best_name


def _get_multiplier(focus_name, concept_names, concepts_db):
    """
    Counts how many related of the focus appear in the related of other concepts.
    Multiplicador = coincidencias + 1
    """
    focus = concepts_db.get(focus_name, {})
    focus_related = set(focus.get("related", []))
    if not focus_related:
        return 1

    coincidences = 0
    for name in concept_names:
        if name == focus_name:
            continue
        other = concepts_db.get(name, {})
        other_related = set(other.get("related", []))
        coincidences += len(focus_related & other_related)

    return coincidences + 1


def _concept_value(name, concepts_db, tag_values, keys, motor="somatic"):
    """
    Calculates the vector of a concept by summing the tag_values of all its
    related[motor]. Accumulation is done in oriented space — each
    factor has intrinsic polarity (ORIENTATION) — and the result is
    returned as pure magnitudes (CCM convention).
    """
    from core.formulas import ORIENTATION, oriented, magnitude
    c = concepts_db.get(name)
    if not c:
        return None

    # Collect all tags of the engine from the related
    tag_counts = {}
    for related_node, branches in c.get("related", {}).items():
        for tag in branches.get(motor, []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    tag_vals = []
    for tag, count in tag_counts.items():
        if tag in tag_values:
            weighted = {k: tag_values[tag][k] * count for k in keys if k in tag_values[tag]}
            tag_vals.append(weighted)

    if not tag_vals:
        return None

    # Average in oriented space to preserve semantics
    result = {}
    for k in keys:
        # Suma de values orientados de cada tag
        total_oriented = sum(oriented(k, v.get(k, 0)) for v in tag_vals)
        avg_oriented   = total_oriented / len(tag_vals)
        result[k]      = magnitude(k, avg_oriented)
    return result


# ── step 2 — memory ──────────────────────────────────────────────────────────

def _memory_vector(focus_name, memory, keys, max_val):
    """
    Searches for the focus in short/medium/long term.
    If found, calculates the median point of the graph (start, peak, end)
    y lo convierte en un vector de interferencia.
    """
    if memory is None:
        return None

    all_memories = (
        list(memory.short_term) +
        list(memory.medium_term) +
        list(memory.long_term)
    )

    matching = [
        e for e in all_memories
        if focus_name in e.get("concepts", [])
    ]

    if not matching:
        return None

    # Take the most relevant — highest peak
    best = max(matching, key=lambda e: e.get("mental_peak", 0) + e.get("somatic_peak", 0))

    graph = best.get("graph", {})
    start = graph.get("start", (0, 0))
    peak  = graph.get("peak",  (0, 0))
    end   = graph.get("end",   (0, 0))

    # Median point of the 3 graph points
    # The graph stores (D, C) — distances
    # We use the peak as the maximum intensity vector
    # and start/end as modulators
    pD, pC = peak
    sD, sC = start
    eD, eC = end

    median_D = (sD + pD + eD) / 3.0
    median_C = (sC + pC + eC) / 3.0

    # Convert distance to vector according to the keys
    # If somatic: project onto (V-I, Lv-Gv)
    # If mental:  project onto (P-A, Er-Rr)
    intensity = (median_D + median_C) / 2.0
    scale     = min(intensity / max_val, 1.0)

    if "V" in keys:
        # Somatic — the past event pushes V or I according to its sign
        vec = {k: 0.0 for k in keys}
        vec["I"]  = scale * max_val * 0.3   # memory de threat sube I
        vec["Lv"] = scale * max_val * 0.2
        return vec
    else:
        # mental — the past event raises A and Er (anguish, emotion)
        vec = {k: 0.0 for k in keys}
        vec["A"]  = scale * max_val * 0.3
        vec["Er"] = scale * max_val * 0.2
        return vec


# ── MAIN SEMANTIC PIPELINE ──────────────────────────────────────────────

def _pre_input_semantic(concept_names, concepts_db, tag_values, keys, max_val, memory=None, motor="somatic"):
    from core.formulas import ORIENTATION, oriented, magnitude, apply_input

    focus_name = _get_focus(concept_names, concepts_db)
    if not focus_name:
        return None

    focus_vec = _concept_value(focus_name, concepts_db, tag_values, keys, motor)
    if not focus_vec:
        return None

    # step 1 — multiplier por related compartidos
    multiplier = _get_multiplier(focus_name, concept_names, concepts_db)

    # apply multiplier en espacio orientado → devolver magnitude
    result = {}
    for k in keys:
        scaled = oriented(k, focus_vec[k]) * multiplier
        result[k] = min(max_val, magnitude(k, scaled))

    # Semi-foci (remaining concepts) enter with weight 0.5 in oriented space
    for name in concept_names:
        if name == focus_name:
            continue
        vec = _concept_value(name, concepts_db, tag_values, keys, motor)
        if not vec:
            continue
        for k in keys:
            current_oriented = oriented(k, result[k])
            extra_oriented   = oriented(k, vec[k]) * 0.5
            combined         = current_oriented + extra_oriented
            result[k]        = min(max_val, magnitude(k, combined))

    # step 2 — memory
    mem_vec = _memory_vector(focus_name, memory, keys, max_val)
    if mem_vec:
        result = apply_input(result, mem_vec, keys)

    result["_focus"]      = focus_name
    result["_multiplier"] = multiplier
    result["_concepts"]   = concept_names
    result["_memory"]     = mem_vec is not None
    result["_pipeline"]   = "semantic"
    return result


# ── receptor PIPELINE ─────────────────────────────────────────────────────────

def _pre_input_receptor(receptor_type, value, zone=None):
    from db.db_receptors import lookup_receptor, lookup_receptor_weighted
    from systems.core_system import update_stat
    match = lookup_receptor_weighted(receptor_type, value, zone) if zone else lookup_receptor(receptor_type, value)
    if not match:
        return None
    update_stat(stat_key=match["stat"], value=value, label=match["label"],
                somatic=match["somatic"], mental=match["mental"])
    result = dict(match["somatic"])
    result.update({"_token": receptor_type, "_type": "receptor", "_label": match["label"],
                   "_stat": match["stat"], "_pipeline": "receptor", "_zone": zone or "unspecified",
                   "_mental": match["mental"]})
    return result


def _pre_input_receptor_mental(receptor_type, value, zone=None):
    from db.db_receptors import lookup_receptor, lookup_receptor_weighted
    from systems.core_system import update_stat
    match = lookup_receptor_weighted(receptor_type, value, zone) if zone else lookup_receptor(receptor_type, value)
    if not match:
        return None
    update_stat(stat_key=match["stat"], value=value, label=match["label"],
                somatic=match["somatic"], mental=match["mental"])
    result = dict(match["mental"])
    result.update({"_token": receptor_type, "_type": "receptor", "_label": match["label"],
                   "_stat": match["stat"], "_pipeline": "receptor", "_zone": zone or "unspecified",
                   "_somatic": match["somatic"]})
    return result


# ── CONTRADICTION DETECTION ───────────────────────────────────────────────

def detect_contradiction(concept_names, concepts_db=None):
    """
    Detects if the scene contains a (subject, action) pair where the action
    does NOT appear in the subject related — absent link in the graph.
    """
    if concepts_db is None:
        from db.db_concepts import CONCEPTS
        concepts_db = CONCEPTS

    subjects = [n for n in concept_names if concepts_db.get(n, {}).get("type") == "subject"]
    actions  = [n for n in concept_names if concepts_db.get(n, {}).get("type") == "action"]

    if not subjects or not actions:
        return {"is_contradiction": False}

    for subj in subjects:
        subj_related = set(concepts_db[subj].get("related", {}).keys())
        for act in actions:
            if act not in subj_related:
                subj_syns = concepts_db[subj].get("synonyms", [subj])
                act_syns  = concepts_db[act].get("synonyms", [act])
                return {
                    "is_contradiction": True,
                    "subject":          subj,
                    "action":           act,
                    "subject_label":    subj,
                    "action_label":     act,
                }

    return {"is_contradiction": False}


# ── PUBLIC API ───────────────────────────────────────────────────────────────

def pre_input_somatic(concept_names, memory=None):
    from db.db_somatic  import TAG_VALUES_SOMATIC, SOMATIC_KEYS, SOMATIC_MAX
    from db.db_concepts import CONCEPTS
    return _pre_input_semantic(concept_names, CONCEPTS, TAG_VALUES_SOMATIC, SOMATIC_KEYS, SOMATIC_MAX, memory, motor="somatic")


def pre_input_mental(concept_names, memory=None):
    from db.db_mental   import TAG_VALUES_MENTAL, MENTAL_KEYS, MENTAL_MAX
    from db.db_concepts import CONCEPTS
    return _pre_input_semantic(concept_names, CONCEPTS, TAG_VALUES_MENTAL, MENTAL_KEYS, MENTAL_MAX, memory, motor="mental")


def pre_input_receptor_somatic(receptor_type, value, zone=None):
    return _pre_input_receptor(receptor_type, value, zone)


def pre_input_receptor_mental(receptor_type, value, zone=None):
    return _pre_input_receptor_mental(receptor_type, value, zone)


def pre_input_receptor_both(receptor_type, value, zone=None):
    from db.db_receptors import lookup_receptor, lookup_receptor_weighted
    from systems.core_system import update_stat
    match = lookup_receptor_weighted(receptor_type, value, zone) if zone else lookup_receptor(receptor_type, value)
    if not match:
        return None
    update_stat(stat_key=match["stat"], value=value, label=match["label"],
                somatic=match["somatic"], mental=match["mental"])
    meta = {"_token": receptor_type, "_type": "receptor", "_label": match["label"],
            "_stat": match["stat"], "_pipeline": "receptor", "_zone": zone or "unspecified"}
    return {"somatic": {**match["somatic"], **meta}, "mental": {**match["mental"], **meta}}
