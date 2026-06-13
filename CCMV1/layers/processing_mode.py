# layers/processing_mode.py — CCM v7
#
# PROCESSING MODE SYSTEM
# ══════════════════════════════════════════════════════════════════════
#
# Determines HOW the mental engine processes information — not WHAT it feels.
# This is a cognitive processing-mode system, not an emotion system.
#
# SOURCE:
#   cx = (Er - Rr) / 2   from mental Cf point
#   cx > 0  →  Emotional dominance  (E)
#   cx < 0  →  Rational dominance   (R)
#   |cx|    →  Dominance intensity
#
# PROCESSING MODES:
#   emotional — reduces inference depth, narrows focus, shortens output
#   rational  — increases inference depth, expands context, lengthens output
#
# INFERENCE DEPTH by mode and tension:
#
#   Emotional:
#     low      → 3   (some reasoning still available)
#     medium   → 2
#     high     → 1
#     critical → 0   (preverbal — somatic output only)
#
#   Rational:
#     low      → 2   (baseline analytical)
#     medium   → 4
#     high     → 6
#     critical → 8   (extended reasoning chain — rumination risk)
#
# PHRASE CONSTRUCTION RULES:
#   Emotional mode:
#     — Use only strongest / most salient concepts
#     — Prefer short templates
#     — Reduce contextual expansion
#     — inference_depth = 0 → no verbal output (somatic dominates)
#
#   Rational mode:
#     — Use concept associations and related chains
#     — Expand reasoning with connectors (if, then, because, therefore)
#     — Allow longer phrase generation up to inference_depth steps
#
# ══════════════════════════════════════════════════════════════════════

# Inference depth tables
_EMOTIONAL_DEPTH = {
    "low":      3,
    "medium":   2,
    "high":     1,
    "critical": 0,
}

_RATIONAL_DEPTH = {
    "low":      2,
    "medium":   4,
    "high":     6,
    "critical": 8,
}

# Dominance threshold — below this |cx|, mode is considered "balanced"
# (no strong E or R pull). Balanced defaults to rational processing.
DOMINANCE_THRESHOLD = 5.0


def get_processing_mode(cfx: float, tension: str) -> dict:
    """
    Calculates processing_mode and inference_depth from mental Cf x-component.

    Parameters
    ----------
    cfx     : float — x-component of mental Cf point (cx)
                      positive = emotional dominance
                      negative = rational dominance
    tension : str   — current mental tension level
                      ("low" | "medium" | "high" | "critical")

    Returns
    -------
    dict with:
        processing_mode   : "emotional" | "rational" | "balanced"
        inference_depth   : int (0–8)
        dominance_axis    : float (|cfx| — strength of mode dominance)
        tension           : str (echo of input tension)
        preverbal         : bool (True when inference_depth == 0)
    """
    abs_cx = abs(cfx)

    if abs_cx < DOMINANCE_THRESHOLD:
        # Balanced — no strong E/R pull. Use rational as default.
        mode = "balanced"
        depth = _RATIONAL_DEPTH.get(tension, 2)
    elif cfx > 0:
        mode  = "emotional"
        depth = _EMOTIONAL_DEPTH.get(tension, 1)
    else:
        mode  = "rational"
        depth = _RATIONAL_DEPTH.get(tension, 2)

    return {
        "processing_mode":  mode,
        "inference_depth":  depth,
        "dominance_axis":   round(abs_cx, 3),
        "tension":          tension,
        "preverbal":        depth == 0,
    }


def build_emotional_phrase(focus_concept: str, tension: str,
                            inference_depth: int, quadrant: str) -> str | None:
    """
    Builds a phrase in emotional processing mode.

    Emotional mode progressively loses linguistic complexity as tension rises:
        low      → "I don't like this."
        medium   → "Stop that."
        high     → "Stop!"
        critical → "No!"
        preverbal (depth=0) → None (somatic output only)

    focus_concept : strongest concept in the scene (from pre_input focus)
    tension       : current mental tension
    inference_depth: 0 = preverbal, 1 = single word, 2 = short phrase, 3 = sentence
    quadrant      : mental quadrant for valence direction
    """
    if inference_depth == 0:
        return None  # preverbal — somatic takes over

    is_negative = quadrant in ("absent-emotional", "absent-rational")
    is_positive = quadrant in ("present-emotional", "present-rational")

    if inference_depth == 1:
        # Single reactive word
        if is_negative:
            return "No!"
        elif is_positive:
            return "Yes!"
        return "Stop!"

    if inference_depth == 2:
        # Short imperative
        if is_negative:
            return "Stop that."
        elif is_positive:
            return "Come on."
        return "Back off."

    if inference_depth >= 3:
        # Short sentence with concept
        if is_negative and focus_concept:
            return f"I don't like this {focus_concept}."
        elif is_positive and focus_concept:
            return f"This {focus_concept} feels right."
        elif is_negative:
            return "I don't like this."
        return "Something feels off."

    return None


def build_rational_phrase(focus_concept: str, tension: str,
                           inference_depth: int, quadrant: str,
                           scene_concepts: list = None) -> str | None:
    """
    Builds a phrase in rational processing mode.

    Rational mode progressively increases linguistic complexity:
        low  (depth=2) → simple explanation
        med  (depth=4) → explanation + one inference
        high (depth=6) → explanation + multiple inferences
        crit (depth=8) → extended reasoning chain (rumination risk)

    focus_concept  : primary concept in the scene
    tension        : current mental tension
    inference_depth: number of reasoning steps to include
    quadrant       : mental quadrant
    scene_concepts : full concept list for secondary references
    """
    if not focus_concept:
        return None

    is_negative = quadrant in ("absent-emotional", "absent-rational")
    is_positive = quadrant in ("present-emotional", "present-rational")

    secondary = [c for c in (scene_concepts or []) if c != focus_concept][:2]

    if inference_depth <= 2:
        # Simple observation
        if is_negative:
            return f"The {focus_concept} is not safe."
        return f"The {focus_concept} is here."

    if inference_depth <= 4:
        # Observation + one inference
        if is_negative:
            context = f" and {secondary[0]}" if secondary else ""
            return (f"The {focus_concept}{context} may represent a threat"
                    f" because it is unknown.")
        context = f" with {secondary[0]}" if secondary else ""
        return (f"The {focus_concept}{context} appears stable"
                f" and can be approached.")

    if inference_depth <= 6:
        # Observation + multiple inferences
        if is_negative:
            ctx = f" along with {secondary[0]}" if secondary else ""
            return (f"The {focus_concept}{ctx} may represent a threat."
                    f" Its presence is unusual. Caution is advisable.")
        ctx = f" near {secondary[0]}" if secondary else ""
        return (f"The {focus_concept}{ctx} creates a favorable condition."
                f" This is manageable. Remaining aware is still useful.")

    # inference_depth >= 8 — extended chain (critical rational)
    if is_negative:
        ctx = f" combined with {secondary[0]}" if secondary else ""
        return (f"If the {focus_concept}{ctx} is real, it may be dangerous."
                f" If it is dangerous, approaching it may not be safe."
                f" If it is not safe, withdrawing is the correct response.")
    ctx = f" alongside {secondary[0]}" if secondary else ""
    return (f"The {focus_concept}{ctx} is present and appears non-threatening."
            f" If it remains stable, engagement is possible."
            f" Monitoring the situation before acting is the rational approach.")
