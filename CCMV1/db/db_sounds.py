# db/db_sounds.py — CCM v8
#
# PREVERBAL SOUND DATABASE
# Maps somatic states → instinctive vocalizations.
#
# These are not words — they are phonetic outputs produced when the somatic
# motor dominates and the mental motor has not yet formed language.
#
# Structure:
#   SOUNDS: tag → sound string
#   STATE_TAGS: somatic state label → list of tags (ordered by priority)
#   QUADRANT_TAGS: (quadrant, tension) → list of tags (fallback)
#
# Selection: STATE_TAGS first, then QUADRANT_TAGS as fallback.
# Multiple tags produce combined sounds (e.g. "iii" + "aaa" → "iii-aaa").

# ── SOUND PRIMITIVES ──────────────────────────────────────────────────────────

SOUNDS = {
    # Simple
    "fear_sharp":       "iiiiii",
    "discomfort":       "eeeeee",
    "pain_open":        "aaaaaaa",
    "wonder":           "ooooooo",
    "resistance":       "uuuuuu",
    "satisfaction":     "mmmmm",
    "doubt":            "nnnnn",
    "relief":           "haaaaaa",
    "caution":          "fffffff",
    "alert":            "sssssss",
    "anger":            "rrrrrrr",
    "effort_heavy":     "ggggggg",
    "rejection":        "kkkkkkk",
    "contempt":         "pffff",
    "disgust":          "ugh",
    "realization":      "ahh",
    "discovery":        "oh!",
    "confusion":        "eh?",

    # Combinations
    "effort_intense":   "unngghhh",
    "bearing_load":     "uuuggghhh",
    "threat_defense":   "grrrrrr",
    "containing":       "hnnnnng",
    "satisfaction_open":"mmm-ah",
    "uncertainty":      "eeehhh",
    "fright_release":   "iii-aaa",
    "contemplation":    "ooohhh",
    "pain_frustration": "aaaugh",
    "curious_positive": "mmmmm...?",
    "effort_complete":  "unngh-ah",
}

# ── STATE → TAGS ──────────────────────────────────────────────────────────────
# Maps somatic state labels (from emotion_mapper.get_somatic_state) to sounds.
# First tag is primary; additional tags combine if tension is high enough.

STATE_SOUNDS = {
    # inviable-localized
    "bracing":                      ["fear_sharp"],
    "threat response":              ["fear_sharp", "alert"],
    "high threat, tachycardia":     ["fear_sharp", "resistance"],
    "system overload":              ["fear_sharp", "effort_intense"],
    "physical collapse":            ["pain_open", "bearing_load"],
    "frozen, cortisol spike":       ["containing"],
    "locked up":                    ["containing"],
    "stiff, restricted":            ["discomfort"],
    "tense, guarded":               ["discomfort", "alert"],
    "stiff":                        ["discomfort"],
    "paralyzed":                    ["containing", "fear_sharp"],
    "pain response suppressed":     ["containing"],

    # inviable-globalized
    "burnout, exhausted":           ["bearing_load"],
    "drained":                      ["bearing_load"],
    "failing":                      ["effort_heavy"],
    "collapse imminent":            ["pain_frustration"],
    "systemic failure":             ["pain_frustration"],
    "total breakdown":              ["pain_open"],
    "collapse":                     ["pain_open"],
    "weakened":                     ["effort_heavy"],
    "low energy":                   ["doubt"],
    "pain override":                ["containing", "pain_open"],

    # viable-localized
    "high threat response":         ["fear_sharp", "alert"],
    "racing pulse, on guard":       ["alert", "resistance"],
    "alert, tense":                 ["alert"],
    "keyed up":                     ["alert"],
    "fight ready":                  ["threat_defense"],
    "mobilized":                    ["resistance"],
    "activated":                    ["alert"],
    "aggressive posture":           ["anger", "threat_defense"],
    "assertive":                    ["anger"],
    "chronic tension":              ["discomfort", "containing"],
    "stressed":                     ["discomfort"],
    "relaxed alert":                ["satisfaction"],
    "at ease":                      ["relief"],
    "physical ease":                ["satisfaction"],
    "muscle tension":               ["resistance"],
    "tense":                        ["discomfort"],
    "ready":                        ["alert"],
    "stable":                       ["satisfaction"],
    "ready":                        ["alert"],
    "calm":                         ["satisfaction"],
    "at rest":                      ["satisfaction"],

    # viable-globalized
    "fleeing":                      ["fright_release"],
    "flight response":              ["fear_sharp", "resistance"],
    "running":                      ["effort_intense"],
    "moving away":                  ["resistance"],
    "energized, open":              ["satisfaction_open"],
    "expansive":                    ["wonder"],
    "warm, connected":              ["satisfaction"],
    "open":                         ["satisfaction"],
    "scattered energy":             ["uncertainty"],
    "overwhelmed body":             ["bearing_load"],
    "energized":                    ["satisfaction"],
}

# ── QUADRANT FALLBACK ─────────────────────────────────────────────────────────
# Used when the state label isn't in STATE_SOUNDS.

QUADRANT_SOUNDS = {
    ("inviable-localized",  "low"):      ["discomfort"],
    ("inviable-localized",  "medium"):   ["fear_sharp"],
    ("inviable-localized",  "high"):     ["fear_sharp", "resistance"],
    ("inviable-localized",  "critical"): ["fright_release"],

    ("inviable-globalized", "low"):      ["doubt"],
    ("inviable-globalized", "medium"):   ["bearing_load"],
    ("inviable-globalized", "high"):     ["pain_open"],
    ("inviable-globalized", "critical"): ["pain_frustration"],

    ("viable-localized",    "low"):      ["alert"],
    ("viable-localized",    "medium"):   ["alert"],
    ("viable-localized",    "high"):     ["threat_defense"],
    ("viable-localized",    "critical"): ["fright_release"],

    ("viable-globalized",   "low"):      ["satisfaction"],
    ("viable-globalized",   "medium"):   ["satisfaction"],
    ("viable-globalized",   "high"):     ["effort_intense"],
    ("viable-globalized",   "critical"): ["bearing_load"],
}


# ── SELECTOR ──────────────────────────────────────────────────────────────────

def get_somatic_sound(state_label: str, quadrant: str, tension: str,
                       chemical_levels: dict = None) -> str:
    """
    Returns the preverbal sound for a somatic state.

    Parameters
    ----------
    state_label     : from emotion_mapper.get_somatic_state()["state"]
    quadrant        : somatic quadrant string
    tension         : "low" | "medium" | "high" | "critical"
    chemical_levels : optional dict — used to refine selection when state
                      label is generic (e.g. "alert, tense" with high adrenaline
                      → fear sound instead of plain alert)

    Returns
    -------
    Sound string (e.g. "iiiiii", "iii-aaa", "grrrrrr")
    """
    chem = chemical_levels or {}

    # Chemical override — if we have specific chemical signatures, use them
    # regardless of the generic state label
    adrena   = chem.get("adrenaline",    0)
    cortisol = chem.get("cortisol",      0)
    noradre  = chem.get("noradrenaline", 0)
    testo    = chem.get("testosterona",  0)

    if "inviable" in quadrant:
        if adrena > 2 or (adrena > 1 and cortisol > 1):
            tags = ["fear_sharp", "resistance"] if tension in ("high","critical") else ["fear_sharp"]
            return _combine(tags, tension)
        if cortisol > 3:
            return SOUNDS["containing"]
    if "viable" in quadrant and testo > 1 and noradre > 1:
        return SOUNDS["threat_defense"]

    tags = STATE_SOUNDS.get(state_label)
    if not tags:
        tags = QUADRANT_SOUNDS.get((quadrant, tension), ["doubt"])

    return _combine(tags, tension)


def _combine(tags: list, tension: str) -> str:
    """Combines tags into a sound string based on tension."""
    if tension in ("low", "medium") or len(tags) == 1:
        return SOUNDS.get(tags[0], "...")
    s1 = SOUNDS.get(tags[0], "")
    s2 = SOUNDS.get(tags[1], "") if len(tags) > 1 else ""
    if s1 and s2:
        return f"{s1}-{s2}"
    return s1 or "..."
