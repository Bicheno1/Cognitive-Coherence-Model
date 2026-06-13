# systems/plasticity_system.py — CCM v5
#
# Plasticity — two-step learning:
#
# STEP 1 — Modify TAG_VALUES (existing)
#   At the end of each cycle, for each active tag in the scene:
#   - Determines how much it changes based on memory history
#   - Determines direction: state rose → sensitization, fell → habituation
#   - Modifies all axes of the tag proportionally
#
#   Deltas by history:
#     first exposure  → DELTA_FIRST   (minimum)
#     medium_term     → DELTA_MEDIUM
#     long_term       → DELTA_LONG
#     nuclear         → DELTA_NUCLEAR (maximum)
#
# step 2 — Comprobar links en db_concepts (nuevo)
#   Only activates if STEP 1 modified any tag.
#   For each active concept, compares its highest activation value
#   with the highest value of each of its related.
#   If the difference is > RELATED_THRESHOLD (20) → breaks the link in related.
#
#   Ejemplo:
#     ghost tiene I=125 (mayor value)
#     danger tiene I=110 (mayor value)
#     |125 - 110| = 15 < 20 → siguen related
#
#     After habituation ghost drops to I=80
#     |80 - 110| = 30 > 20 → danger sale de related de ghost
#
# OPENING (dist_mental < 30):
#   In opening range the plasticity learns at maximum — DELTA_NUCLEAR
#   independently of history de memory.

from db.db_somatic  import TAG_VALUES_SOMATIC, SOMATIC_KEYS, SOMATIC_MAX
from db.db_mental   import TAG_VALUES_MENTAL,  MENTAL_KEYS,  MENTAL_MAX
from db.db_concepts import CONCEPTS

DELTA_FIRST   = 0.02
DELTA_MEDIUM  = 0.06
DELTA_LONG    = 0.12
DELTA_NUCLEAR = 0.25

MIN_VAL        = 0.01
MIN_CHANGE_MAG = 0.15

# step 2 — divergence threshold to break a link in related
RELATED_THRESHOLD = 20.0


# ── step 1 HELPERS ────────────────────────────────────────────────────────────

def _get_delta(concept_name, active_concepts, memory, dist_mental=None):
    # Full opening → maximum learning
    if dist_mental is not None and dist_mental < 30.0:
        return DELTA_NUCLEAR

    in_long    = False
    is_nuclear = False
    for event in memory.long_term:
        overlap = set(event["concepts"]) & set(active_concepts)
        if overlap:
            in_long = True
            if event["is_nuclear"]:
                is_nuclear = True
                break

    if is_nuclear:   return DELTA_NUCLEAR
    if in_long:      return DELTA_LONG

    in_medium = any(
        set(e["concepts"]) & set(active_concepts)
        for e in memory.medium_term
    )
    if in_medium:    return DELTA_MEDIUM
    return DELTA_FIRST


def _direction(state_before, state_after, keys):
    mag_before = sum(state_before.get(k, 0) ** 2 for k in keys) ** 0.5
    mag_after  = sum(state_after.get(k, 0)  ** 2 for k in keys) ** 0.5
    diff = mag_after - mag_before
    if abs(diff) < MIN_CHANGE_MAG:
        return 0
    return 1 if diff > 0 else -1


def _modify_tag(tag_name, tag_db, delta, direction, max_val):
    if tag_name not in tag_db:
        return
    for k in list(tag_db[tag_name].keys()):
        old = tag_db[tag_name][k]
        tag_db[tag_name][k] = max(MIN_VAL, min(max_val, old + delta * direction))


def _concept_max_value(concept_name, tag_db, keys):
    """
    Calculates the highest activation value of a concept
    by summing its tag vectors and taking the maximum component.
    """
    c = CONCEPTS.get(concept_name, {})
    # Collect all tags of the concept from its related
    tags = set()
    for branches in c.get("related", {}).values():
        for motor in ("somatic", "mental"):
            tags.update(branches.get(motor, []))

    if not tags:
        return 0.0

    total = {k: 0.0 for k in keys}
    count = 0
    for tag in tags:
        if tag in tag_db:
            for k in keys:
                total[k] += tag_db[tag].get(k, 0.0)
            count += 1

    if count == 0:
        return 0.0

    avg = {k: total[k] / count for k in keys}
    return max(avg.values())


# ── step 2 — COMPROBAR LINKS EN db_concepts ───────────────────────────────────

def _check_related_links(active_concepts, tag_db, keys):
    """
    For each active concept, compares its highest activation value
    with each related. If the difference > RELATED_THRESHOLD → breaks the link.

    Returns dict: {concept: [related_removidos]}
    """
    removed = {}

    for concept_name in active_concepts:
        c = CONCEPTS.get(concept_name)
        if not c:
            continue

        concept_max = _concept_max_value(concept_name, tag_db, keys)
        to_remove   = []

        for related_name in list(c.get("related", {}).keys()):
            related_max = _concept_max_value(related_name, tag_db, keys)
            if abs(concept_max - related_max) > RELATED_THRESHOLD:
                to_remove.append(related_name)

        if to_remove:
            for r in to_remove:
                del c["related"][r]
            removed[concept_name] = to_remove

    return removed


# ── PUBLIC API ───────────────────────────────────────────────────────────────

def apply_plasticity(active_concepts, memory, state_before_s, state_after_s,
                     state_before_m, state_after_m, dist_mental=None):
    """
    Llama al final de cada ciclo.

    active_concepts : list[str]
    memory          : MemorySystem
    state_before_*  : dict with engine values before the cycle
    state_after_*   : dict with engine values after the cycle
    dist_mental     : current mental distance (to detect opening)
    """
    changed = {
        "somatic":      {},
        "mental":       {},
        "links_removed": {},
    }

    dir_s = _direction(state_before_s, state_after_s, SOMATIC_KEYS)
    dir_m = _direction(state_before_m, state_after_m, MENTAL_KEYS)

    if dir_s == 0 and dir_m == 0:
        return changed  # nada significativo — no modifica

    # ── step 1 ────────────────────────────────────────────────────────────────
    for concept_name in active_concepts:
        c = CONCEPTS.get(concept_name)
        if not c:
            continue

        delta = _get_delta(concept_name, active_concepts, memory, dist_mental)

        # Somatic — tags from related[somatic]
        if dir_s != 0:
            tags_s = set()
            for branches in c.get("related", {}).values():
                tags_s.update(branches.get("somatic", []))
            for tag_name in tags_s:
                if tag_name in TAG_VALUES_SOMATIC:
                    _modify_tag(tag_name, TAG_VALUES_SOMATIC, delta, dir_s, SOMATIC_MAX)
                    changed["somatic"][tag_name] = {
                        "delta":     round(delta * dir_s, 4),
                        "direction": "up" if dir_s > 0 else "down",
                        "new_I":     round(TAG_VALUES_SOMATIC[tag_name].get("I", 0), 4),
                        "new_V":     round(TAG_VALUES_SOMATIC[tag_name].get("V", 0), 4),
                    }

        # Mental — tags from related[mental]
        if dir_m != 0:
            tags_m = set()
            for branches in c.get("related", {}).values():
                tags_m.update(branches.get("mental", []))
            for tag_name in tags_m:
                if tag_name in TAG_VALUES_MENTAL:
                    _modify_tag(tag_name, TAG_VALUES_MENTAL, delta, dir_m, MENTAL_MAX)
                    changed["mental"][tag_name] = {
                        "delta":     round(delta * dir_m, 4),
                        "direction": "up" if dir_m > 0 else "down",
                        "new_A":     round(TAG_VALUES_MENTAL[tag_name].get("A", 0), 4),
                        "new_P":     round(TAG_VALUES_MENTAL[tag_name].get("P", 0), 4),
                    }

    # ── STEP 2 — only if step 1 modified anything ──────────────────────────────
    if changed["somatic"] or changed["mental"]:
        # Check somatic links
        removed_s = _check_related_links(active_concepts, TAG_VALUES_SOMATIC, SOMATIC_KEYS)
        # Comprobar links mentales
        removed_m = _check_related_links(active_concepts, TAG_VALUES_MENTAL, MENTAL_KEYS)

        all_removed = {}
        for k, v in {**removed_s, **removed_m}.items():
            all_removed.setdefault(k, [])
            for r in v:
                if r not in all_removed[k]:
                    all_removed[k].append(r)

        changed["links_removed"] = all_removed

    return changed
