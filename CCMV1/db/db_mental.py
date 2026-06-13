# db/db_mental.py — CCM v5
# Functional scale: 0–50 normal use · 50–100 intense · 100–150 extreme · 150–200 collapse
# MENTAL_BASE neutral: P=12 A=3 Er=6 Rr=8

MENTAL_KEYS      = ["P", "A", "Er", "Rr"]
MENTAL_MAX       = 200
MENTAL_APERTURE  = 12

MENTAL_BASE = {
    "P":  12,
    "A":   3,
    "Er":  6,
    "Rr":  8
}

# ── TAG VALUES ─────────────────────────────────────────────────────────────────
# Calibration reference:
#   darkness       → A=18 Er=10  (threat incierta, baja racionalidad)
#   threat directa → A=40 Er=30  (fear extremo, reaction emotional)
#   ghost           → A=34 Er=32  (irrational fear, logic break)
#   person amada   → P=22 Rr=8   (apego, estabilidad positiva)
#   money/resource  → P=16 Rr=20  (control, rational planning)

TAG_VALUES_MENTAL = {

    # ── TERROR / DISSOCIATION ──────────────────────────────────────────────────
    "terror":            {"P":  2, "A": 38, "Er": 34, "Rr":  4},  # maximum functional fear
    "anguish":          {"P":  4, "A": 26, "Er": 28, "Rr":  6},  # intense anxiety
    "confusion":         {"P":  6, "A": 20, "Er": 22, "Rr":  8},  # disorientation
    "disbelief":      {"P":  5, "A": 22, "Er": 18, "Rr": 10},  # cannot process
    "cognitive_threat": {"P":  3, "A": 28, "Er": 26, "Rr":  6},  # threat to logic
    "overflow":          {"P":  2, "A": 36, "Er": 38, "Rr":  3},  # emotional collapse

    # ── ALERT / VIGILANCE ───────────────────────────────────────────────────
    "hypervigilance":   {"P": 14, "A": 12, "Er": 24, "Rr": 10},  # constant scanning
    "alert":            {"P": 12, "A": 10, "Er": 20, "Rr": 12},  # heightened attention
    "suspicion":          {"P": 10, "A": 14, "Er": 16, "Rr": 14},  # distrust
    "anticipation":      {"P": 16, "A":  8, "Er": 18, "Rr": 16},  # future projection

    # ── CALM / CLARITY ──────────────────────────────────────────────────────
    "relief":            {"P": 20, "A":  2, "Er":  8, "Rr": 22},  # tension releasing
    "mental_security":  {"P": 22, "A":  2, "Er":  5, "Rr": 24},  # cognitive stability
    "clarity":          {"P": 20, "A":  2, "Er":  6, "Rr": 22},  # clear mind
    "trust":         {"P": 18, "A":  3, "Er":  8, "Rr": 20},  # inner certainty

    # ── PURE EMOTIONAL ────────────────────────────────────────────────────────
    "affection":            {"P": 22, "A":  2, "Er": 24, "Rr": 10},  # emotional bond
    "loneliness":           {"P":  8, "A": 18, "Er": 20, "Rr":  8},  # absence of bond
    "guilt":             {"P":  9, "A": 16, "Er": 22, "Rr": 10},  # self-reproach
    "curiosity":        {"P": 18, "A":  4, "Er": 16, "Rr": 18},  # mental exploration
    "sadness":          {"P":  6, "A": 20, "Er": 18, "Rr": 10},  # loss / grief
    "joy":           {"P": 24, "A":  1, "Er": 28, "Rr": 12},  # emotional wellbeing

    # ── PROCESSING ─────────────────────────────────────────────────────────
    "analysis":          {"P": 18, "A":  2, "Er":  6, "Rr": 28},  # pure reasoning
    "memory":            {"P": 14, "A":  8, "Er": 14, "Rr": 16},  # memory evocation
    "denial":          {"P":  5, "A": 24, "Er": 14, "Rr": 10},  # refuses to accept the information
    "acceptance":        {"P": 18, "A":  4, "Er": 10, "Rr": 22},  # integration

    # ── MUSIC / MELODY ──────────────────────────────────────────────────────
    "mental_melody":    {"P": 3, "A": 1, "Er": 4, "Rr": 2},
    "contemplation":    {"P": 2, "A": 1, "Er": 3, "Rr": 3},
    "gentle_resonance": {"P": 4, "A": 0, "Er": 3, "Rr": 2},
    # ── MOTIVATIONAL / BEHAVIORAL ─────────────────────────────────────────────
    # Behavioral tags — drive to seek something to reduce threat
    "seek_light":        {"P":  8, "A": 22, "Er": 20, "Rr":  6},  # seek light/orientation under fear
    "seek_person":       {"P": 12, "A": 18, "Er": 16, "Rr":  8},  # seek safe presence
    "seek_exit":         {"P":  6, "A": 26, "Er": 24, "Rr":  4},  # seek exit/escape
    "traumatic_memory":  {"P":  4, "A": 30, "Er": 28, "Rr":  6},  # traumatic memory activation

    # ── CALM / RECOVERY ────────────────────────────────────────────────────────
    "cognitive_calm":    {"P": 22, "A":  2, "Er":  6, "Rr": 24},  # active cognitive calm
    "mental_clarity":    {"P": 20, "A":  2, "Er":  8, "Rr": 22},  # recovered mental clarity
    "security":          {"P": 24, "A":  2, "Er":  6, "Rr": 26},  # sense of security

    # ── CONCEPT DIRECT VALUES ─────────────────────────────────────────────────
    # Mental signature of each concept — the cognitive baseline response.
    # Referenced as "self" branch in db_concepts.
    #
    # Calibration logic:
    #   ghost   → high A/Er (irrational threat, logic fails, emotional spike)
    #   dark    → moderate A/Er (uncertainty, fear response without object)
    #   room    → low A, mild Er (containment pressure, anticipation)
    #   person  → moderate P/Rr (presence of other, social grounding)
    #   light   → moderate P/Rr (orientation restored, clarity signal)

    "concept_ghost":   {"P":  3, "A": 32, "Er": 30, "Rr":  4},  # impossible entity — logic break
    "concept_dark":    {"P":  6, "A": 18, "Er": 16, "Rr":  8},  # absence of light — diffuse fear
    "concept_room":    {"P":  8, "A":  8, "Er": 10, "Rr": 12},  # enclosed context — mild anticipation
    "concept_person":  {"P": 18, "A":  4, "Er": 10, "Rr": 16},  # human presence — relational anchor
    "concept_light":   {"P": 16, "A":  3, "Er":  8, "Rr": 18},  # visible light — clarity/security

    # ── EXISTENTIAL REFLECTION ─────────────────────────────────────────────────
    "mortality":         {"P":  4, "A": 22, "Er": 20, "Rr": 16},  # awareness of death
    "identity":         {"P": 16, "A":  2, "Er": 10, "Rr": 18},  # sense of self
}
