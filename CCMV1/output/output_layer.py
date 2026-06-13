# output/output_layer.py — TULIO

VERBAL_SOMATIC = {
    "viable-localized": {
        "low":      ["let's go", "come on", "moving"],
        "medium":   ["move", "now", "fast"],
        "high":     ["go!", "now!", "move!"],
        "critical": ["Aaaaaaah!", "Aaaaaaah!", "Aaaaaaah!"],
    },
    "viable-globalized": {
        "low":      ["okay", "yes", "fine"],
        "medium":   ["easy", "I'm here", "it's okay"],
        "high":     ["breathe", "it's fine", "calm"],
        "critical": ["...", "yes...", "okay..."],
    },
    "inviable-localized": {
        "low":      ["what was that", "wait", "hey"],
        "medium":   ["no", "get back", "stop"],
        "high":     ["no!", "get away!", "out!"],
        "critical": ["Aaaaaaah!", "Aaaaaaah!", "Aaaaaaah!"],
    },
    "inviable-globalized": {
        "low":      ["...", "I know", "nothing"],
        "medium":   ["I can't", "enough", "stop"],
        "high":     ["...", "no more", ""],
        "critical": ["", "...", ""],
    },
}

VERBAL_MENTAL = {
    "viable-localized": {
        "low":      ["I'm glad to be here", "this feels important"],
        "medium":   ["something moves me", "I feel it strongly"],
        "high":     ["this matters a lot", "I need to say it"],
        "critical": ["I can't hold it", "I have to act"],
    },
    "viable-globalized": {
        "low":      ["I understand what's happening", "it makes sense"],
        "medium":   ["I can see the situation", "let's analyze this"],
        "high":     ["what's happening is...", "the situation requires..."],
        "critical": ["I need to evaluate every step", "I must be precise"],
    },
    "inviable-localized": {
        "low":      ["something's not right", "I don't feel good about this"],
        "medium":   ["this worries me", "something feels wrong"],
        "high":     ["I can't handle this", "it's overwhelming me"],
        "critical": ["", ""],   # mind frozen — total blank
    },
    "inviable-globalized": {
        "low":      ["it doesn't matter", "whatever"],
        "medium":   ["nothing to do", "it's pointless"],
        "high":     ["...", "no way out"],
        "critical": ["", ""],
    },
    "present-emotional": {
        "low":      ["I'm here", "this feels alive"],
        "medium":   ["something moves me", "I feel it strongly"],
        "high":     ["I can't contain it", "it burns inside"],
        "critical": ["I have to act", "I can't hold it"],
    },
    "present-rational": {
        "low":      ["I understand", "it makes sense"],
        "medium":   ["I can see what's happening", "let me think"],
        "high":     ["the situation is clear", "I need to be precise"],
        "critical": ["I must evaluate every step", "I need clarity now"],
    },
    "absent-emotional": {
        "low":      ["something feels off", "I don't know"],
        "medium":   ["this worries me", "something's wrong"],
        "high":     ["I can't handle this", "it's too much"],
        "critical": ["", ""],
    },
    "absent-rational": {
        "low":      ["it doesn't matter", "whatever"],
        "medium":   ["nothing to do", "pointless"],
        "high":     ["...", "no way out"],
        "critical": ["", ""],
    },
}

MOVEMENT_SOMATIC = {
    "viable-localized": {
        "steps": ["orient_body_toward_target", "activate_upper_body", "project_weight_forward", "execute_action"],
        "low":      [0, 1, 2, 3],
        "medium":   [0, 2, 3],
        "high":     [0, 3],
        "critical": [3],
        "speed": {"low": 1.0, "medium": 1.4, "high": 1.8, "critical": 2.5},
    },
    "viable-globalized": {
        "steps": ["open_posture", "lower_shoulders", "deep_breath", "expansive_movement"],
        "low":      [0, 1, 2, 3],
        "medium":   [0, 1, 3],
        "high":     [0, 3],
        "critical": [0],
        "speed": {"low": 0.7, "medium": 0.9, "high": 1.1, "critical": 1.3},
    },
    "inviable-localized": {
        "steps": ["detect_threat", "contract_core", "protect_center", "flight"],
        "low":      [0, 1, 2, 3],
        "medium":   [0, 2, 3],
        "high":     [0, 3],
        "critical": [3],
        "speed": {"low": 1.2, "medium": 1.6, "high": 2.2, "critical": 3.0},
    },
    "inviable-globalized": {
        "steps": ["reduce_movement", "lower_head", "close_posture", "stillness"],
        "low":      [0, 1, 2, 3],
        "medium":   [1, 2, 3],
        "high":     [2, 3],
        "critical": [3],
        "speed": {"low": 0.5, "medium": 0.4, "high": 0.3, "critical": 0.1},
    },
}

MOVEMENT_MENTAL = {
    "viable-localized": {
        "steps": ["direct_gaze_with_intent", "activate_expression", "approach_gesture", "move_toward_target"],
        "low":      [0, 1, 2, 3],
        "medium":   [0, 1, 2, 3],
        "high":     [0, 2, 3],
        "critical": [0, 3],
        "speed": {"low": 0.9, "medium": 1.1, "high": 1.3, "critical": 1.6},
    },
    "viable-globalized": {
        "steps": ["neutral_stable_posture", "evaluating_gaze", "analysis_gesture", "precise_movement"],
        "low":      [0, 1, 2, 3],
        "medium":   [0, 1, 2, 3],
        "high":     [0, 1, 3],
        "critical": [0, 3],
        "speed": {"low": 0.8, "medium": 1.0, "high": 1.1, "critical": 1.2},
    },
    "inviable-localized": {
        "steps": ["scattered_gaze", "facial_tension", "protective_gesture", "frozen"],
        "low":      [0, 1, 2, 3],
        "medium":   [0, 1, 3],
        "high":     [0, 3],
        "critical": [3],
        "speed": {"low": 1.1, "medium": 1.4, "high": 1.8, "critical": 2.0},
    },
    "inviable-globalized": {
        "steps": ["empty_gaze", "flat_expression", "no_gesture", "mental_stillness"],
        "low":      [0, 1, 2, 3],
        "medium":   [1, 2, 3],
        "high":     [2, 3],
        "critical": [3],
        "speed": {"low": 0.6, "medium": 0.4, "high": 0.2, "critical": 0.1},
    },
    # Real mental nomenclature
    "present-emotional": {
        "steps": ["direct_gaze_with_intent", "activate_expression", "approach_gesture", "move_toward_target"],
        "low":      [0, 1, 2, 3], "medium": [0, 1, 2, 3], "high": [0, 2, 3], "critical": [0, 3],
        "speed": {"low": 0.9, "medium": 1.1, "high": 1.3, "critical": 1.6},
    },
    "present-rational": {
        "steps": ["neutral_stable_posture", "evaluating_gaze", "analysis_gesture", "precise_movement"],
        "low":      [0, 1, 2, 3], "medium": [0, 1, 2, 3], "high": [0, 1, 3], "critical": [0, 3],
        "speed": {"low": 0.8, "medium": 1.0, "high": 1.1, "critical": 1.2},
    },
    "absent-emotional": {
        "steps": ["scattered_gaze", "facial_tension", "protective_gesture", "frozen"],
        "low":      [0, 1, 2, 3], "medium": [0, 1, 3], "high": [0, 3], "critical": [3],
        "speed": {"low": 1.1, "medium": 1.4, "high": 1.8, "critical": 2.0},
    },
    "absent-rational": {
        "steps": ["empty_gaze", "flat_expression", "no_gesture", "mental_stillness"],
        "low":      [0, 1, 2, 3], "medium": [1, 2, 3], "high": [2, 3], "critical": [3],
        "speed": {"low": 0.6, "medium": 0.4, "high": 0.2, "critical": 0.1},
    },
}

import random

def get_tension_somatic(distance):
    """
    Somatic state by distance to center.
    Scale 0-400 per variable → theoretical maximum distance ~566.
      low        0–40
      normal    40–100
      active   100–180
      saturated 180–340
      colapso  340+
    """
    if distance < 40:   return "low"
    elif distance < 100: return "medium"
    elif distance < 180: return "high"
    else:                return "critical"

def get_tension_mental(distance):
    """
    Mental state by distance to center.
    Scale 0-200 per variable → theoretical maximum distance ~283.
      low        0–20
      normal    20–50
      active    50–90
      saturated  90–170
      collapse  170+
    """
    if distance < 20:   return "low"
    elif distance < 50:  return "medium"
    elif distance < 90:  return "high"
    else:                return "critical"

def get_tension_label(distance, motor="mental"):
    """Compatibility wrapper — use get_tension_somatic / get_tension_mental directly."""
    if motor == "somatic":
        return get_tension_somatic(distance)
    return get_tension_mental(distance)

def generate_output(state, core_active_rules=None, concept_names=None,
                     chemical_levels=None):
    s = state["somatic"]
    m = state["mental"]

    s_dist = s["distance"]
    m_dist = m["distance"]
    s_quad = s["sector"]["quadrant"]
    m_quad = m["sector"]["quadrant"]
    s_state = s.get("state", {})

    s_tension = get_tension_somatic(s_dist)
    m_tension = get_tension_mental(m_dist)

    somatic_dominates = s_dist >= m_dist

    # ── VERBAL ────────────────────────────────────────────────────────────────
    # Two independent channels — both are always computed:
    #   verbal_s → preverbal sound from the somatic motor (sounds DB)
    #   verbal_m → structured language from the mental motor (phrase_builder)

    # Somatic channel — always sound
    verbal_s = get_verbal_somatic(s_state, s_dist, chemical_levels)

    # Mental channel — always language
    verbal_m = None
    if concept_names:
        from output.phrase_builder import build_phrase, build_reactive_phrase
        from layers.processing_mode import get_processing_mode

        # Identity first
        verbal_m = build_phrase(concept_names, core_active_rules or [], m_dist)

        # If no identity phrase, use reactive phrase
        if not verbal_m:
            pm = get_processing_mode(m["sector"].get("cfx", 0), m_tension)
            if not pm["preverbal"]:
                from db.db_concepts import CONCEPTS as _C
                _counts = {}
                for _cn in concept_names:
                    for _em in _C.get(_cn, {}).get("related", {}).keys():
                        _counts[_em] = _counts.get(_em, 0) + 1
                m_emotion = max(_counts, key=_counts.get) if _counts else ""
                verbal_m = build_reactive_phrase(
                    active_concepts = concept_names,
                    cfx             = m["sector"].get("cfx", 0),
                    tension         = m_tension,
                    quadrant        = m_quad,
                    dist_mental     = m_dist,
                    emotion         = m_emotion,
                )

    dominant = "somatic" if somatic_dominates else "mental"

    # ── MOVEMENT ──────────────────────────────────────────────────────────────
    if somatic_dominates:
        mov_data = MOVEMENT_SOMATIC[s_quad]
        step_idx = mov_data[s_tension]
        steps    = [mov_data["steps"][i] for i in step_idx]
        speed    = mov_data["speed"][s_tension]
    else:
        mov_data = MOVEMENT_MENTAL.get(m_quad, MOVEMENT_MENTAL["viable-localized"])
        step_idx = mov_data[m_tension]
        steps    = [mov_data["steps"][i] for i in step_idx]
        speed    = mov_data["speed"][m_tension]

    return {
        "dominant": dominant,
        "verbal_s": verbal_s,
        "verbal_m": verbal_m,
        "verbal":   verbal_s if somatic_dominates else (verbal_m or "..."),
        "movement": {
            "steps":   steps,
            "speed":   speed,
            "tension": s_tension if somatic_dominates else m_tension,
        }
    }


# ── DIRECT API FOR CYCLE_MANAGER ─────────────────────────────────────────────

def get_verbal_somatic(s_state: dict, s_dist: float,
                        chemical_levels: dict = None) -> str:
    """
    Returns the preverbal somatic sound based on current somatic state.
    Uses db_sounds to select the appropriate vocalization.
    """
    from layers.quadrant_reader import read_somatic_sector
    from layers.emotion_mapper  import get_somatic_state
    from db.db_sounds           import get_somatic_sound

    sector   = read_somatic_sector(s_state)
    quadrant = sector.get("quadrant", "viable-localized")
    tension  = get_tension_somatic(s_dist)

    V  = s_state.get("V",  0)
    I  = s_state.get("I",  0)
    Lv = s_state.get("Lv", 0)
    Gv = s_state.get("Gv", 0)
    cx = (Lv - Gv) / 2
    cy = (V  - I)  / 2

    em = get_somatic_state(cx, cy, chemical_levels or {})
    state_label = em.get("state", "")

    return get_somatic_sound(state_label, quadrant, tension)


def get_verbal_mental(m_state: dict, m_dist: float) -> str:
    """Returns the mental verbal based on sector and tension."""
    import random
    from layers.quadrant_reader import read_mental_sector
    sector   = read_mental_sector(m_state)
    quadrant = sector.get("quadrant", "present-rational")
    tension  = get_tension_mental(m_dist)
    options  = VERBAL_MENTAL.get(quadrant, {}).get(tension, ["..."])
    return random.choice(options) if options else "..."
