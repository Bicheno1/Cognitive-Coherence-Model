# motors/mind_stats.py — CCM v5
#
# MIND STATS — mental/identity statistics of the host
# Same behavior as vitality_stats but influences the internal mental engine.
#
# Scale 0–10 (same as vitality):
#   10 = optimal state
#    5 = neutral / baseline
#    0 = collapse / crisis
#
# Each stat decays slowly toward its baseline per tick (history markers).
# When a stat drops, it generates pressure on the internal mental engine {P, A, Er, Rr}.
# Pressure is the push received by internal_mental to compensate or react.
#
# STATS:
#   company   — social companionship
#   purpose   — motivation / meaning
#   security  — security existencial
#   structure — orden internal / rutina
#   sanity    — lucidez / coherencia mental

MENTAL_KEYS = ["P", "A", "Er", "Rr"]

# ── STATS DEFINITION ───────────────────────────────────────────────────────
# decay_per_tick : how much it drops per tick toward baseline (very slow)
# baseline       : natural equilibrium value of the host
# mental_push    : pressure generated on {P,A,Er,Rr} when stat is at 0
#                  (scaled by (1 - value/10) — the lower the value, the more pressure)

_STATS = {
    "company": {
        "value":         7.5,
        "baseline":      7.5,
        "decay_per_tick": 0.025,
        # loneliness → raises A (anxiety), lowers Rr (reactive reason)
        "mental_push":   {"P": 0, "A": 80, "Er": 0,  "Rr": 50},
    },
    "purpose": {
        "value":         7.0,
        "baseline":      7.0,
        "decay_per_tick": 0.015,
        # directionless → raises A, raises Er (existential anguish)
        "mental_push":   {"P": 0, "A": 70, "Er": 60, "Rr": 0},
    },
    "security": {
        "value":         8.0,
        "baseline":      8.0,
        "decay_per_tick": 0.020,
        # insecurity → raises A, raises Er
        "mental_push":   {"P": 0, "A": 60, "Er": 70, "Rr": 0},
    },
    "structure": {
        "value":         7.0,
        "baseline":      7.0,
        "decay_per_tick": 0.018,
        # internal chaos → raises A, lowers Rr
        "mental_push":   {"P": 0, "A": 50, "Er": 0,  "Rr": 70},
    },
    "sanity": {
        "value":         9.0,
        "baseline":      9.0,
        "decay_per_tick": 0.010,
        # dissociation → raises Er, lowers Rr
        "mental_push":   {"P": 0, "A": 40, "Er": 80, "Rr": 60},
    },
}

# Labels by range (0–10)
_LABELS = {
    "company":   [(8, "accompanied"),  (6, "ok"),         (4, "alone"),
                  (2, "very_alone"),  (0, "isolated")],
    "purpose":   [(8, "motivated"),   (6, "ok"),         (4, "directionless"),
                  (2, "apathetic"),   (0, "nihilistic")],
    "security":  [(8, "secure"),      (6, "ok"),         (4, "insecure"),
                  (2, "anxious"),     (0, "terrified")],
    "structure": [(8, "ordered"),     (6, "ok"),         (4, "disordered"),
                  (2, "chaotic"),     (0, "collapsed")],
    "sanity":    [(8, "lucid"),       (6, "ok"),         (4, "confused"),
                  (2, "dissociated"), (0, "collapsed")],
}


def _label(name, value):
    for threshold, lbl in _LABELS.get(name, [(5, "ok"), (0, "critical")]):
        if value >= threshold:
            return lbl
    return _LABELS[name][-1][1]


# ── MIND STATS ────────────────────────────────────────────────────────────────

class MindStats:
    def __init__(self):
        self.stats = {k: dict(v) for k, v in _STATS.items()}

    def tick(self):
        """Slow decay toward baseline per tick."""
        for name, s in self.stats.items():
            diff = s["baseline"] - s["value"]
            s["value"] += diff * s["decay_per_tick"]
            s["value"] = max(0.0, min(10.0, s["value"]))

    def update(self, name: str, delta: float):
        """Modifies a stat by an event. positive delta = improvement, negative = damage."""
        if name in self.stats:
            s = self.stats[name]
            s["value"] = max(0.0, min(10.0, s["value"] + delta))

    def get(self, name: str) -> dict:
        return self.stats.get(name, {})

    def all(self) -> dict:
        return {k: round(v["value"], 3) for k, v in self.stats.items()}

    def get_mental_pressure(self) -> dict:
        """
        OUTPUTS: mental pressure {P, A, Er, Rr} toward the internal mental engine.
        Each stat generates pressure proportional to how far below its baseline it is.
        stat en baseline (10) → push = 0
        stat en 0            → push = mental_push completo
        """
        result = {k: 0.0 for k in MENTAL_KEYS}
        for name, s in self.stats.items():
            deficit = max(0.0, s["baseline"] - s["value"]) / s["baseline"]
            push = s["mental_push"]
            for k in MENTAL_KEYS:
                result[k] += push.get(k, 0) * deficit
        return result

    def core_identity_context(self) -> dict:
        """Context for core_identity — mental vulnerability/resilience."""
        se = self.stats["security"]["value"] / 10.0
        sa = self.stats["sanity"]["value"]   / 10.0
        return {
            "resilience":   round((se + sa) / 2.0, 4),
            "isolated":     self.stats["company"]["value"]  < 3.0,
            "purposeless":  self.stats["purpose"]["value"]  < 3.0,
            "chaotic":      self.stats["structure"]["value"] < 3.0,
            "dissociated":  self.stats["sanity"]["value"]   < 3.0,
            "raw":          self.all(),
        }

    def status(self) -> dict:
        out = {}
        for name, s in self.stats.items():
            out[name] = {
                "value": round(s["value"], 3),
                "label": _label(name, s["value"]),
            }
        return out

    def summary_line(self) -> str:
        parts = [f"{n}={v['value']:.1f}({_label(n, v['value'])})"
                 for n, v in self.stats.items()]
        return " | ".join(parts)
