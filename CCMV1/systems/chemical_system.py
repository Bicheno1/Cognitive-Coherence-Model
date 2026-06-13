# systems/chemical_system.py — CCM v5
#
# Chemical DB with vectors calibrated by level (x1, x5, x10).
# The circulating level is continuous (0.0–10.0).
# The push is interpolated between the three points of the table.
#
# DECAY:
#   decay_factor = 0.5 ^ (1 / half_life)
#   level_next   = level_current * decay_factor
#
# PUSH:
#   Given a level L, it interpolates linearly between the three points:
#     L in [0,1]   → between zero and x1
#     L in [1,5]   → between x1 and x5
#     L in [5,10]  → between x5 and x10

import math

SOMATIC_KEYS = ["V", "I", "Lv", "Gv"]

# ── CHEMICAL DB ─────────────────────────────────────────────────────────────
# Each chemical has:
#   half_life   : cycles to drop to 50%
#   max_level   : accumulation ceiling (in level units)
#   triggers    : concepts that release it (1 unit per trigger)
#   vital_triggers: needs that release it when they drop below threshold
#   levels      : vectors {V,I,Lv,Gv} at x1, x5, x10
#                 positive values = add, negative values = subtract

CHEMICALS = {

    "adrenaline": {
        "half_life":  3,
        "max_level":  10.0,
        "triggers":   ["danger", "ghost", "threat", "scared", "attack", "shock"],
        "vital_triggers": [("temperature", 2.0)],
        "levels": {
            1:  {"V": +6,  "I": -2,  "Lv": +8,  "Gv": +2},
            5:  {"V": +20, "I": -8,  "Lv": +28, "Gv": +10},
            10: {"V": +40, "I": -15, "Lv": +55, "Gv": +20},
        },
    },

    "dopamine": {
        "half_life":  4,
        "max_level":  10.0,
        "triggers":   ["food", "safe", "calm", "reward", "win", "goal", "home"],
        "vital_triggers": [],
        "levels": {
            1:  {"V": +8,  "I": -1,  "Lv": +10, "Gv": +3},
            5:  {"V": +22, "I": -4,  "Lv": +26, "Gv": +10},
            10: {"V": +45, "I": -8,  "Lv": +50, "Gv": +18},
        },
    },

    "serotonin": {
        "half_life":  10,
        "max_level":  10.0,
        "triggers":   ["calm", "safe", "light", "breathe", "quiet", "place"],
        "vital_triggers": [],
        "levels": {
            1:  {"V": +10, "I": -4,  "Lv": +8,  "Gv": +6},
            5:  {"V": +25, "I": -10, "Lv": +18, "Gv": +18},
            10: {"V": +40, "I": -18, "Lv": +25, "Gv": +30},
        },
    },

    "oxytocin": {
        "half_life":  8,
        "max_level":  10.0,
        "triggers":   ["person", "safe", "calm", "breathe"],
        "vital_triggers": [],
        "levels": {
            1:  {"V": +7,  "I": -2,  "Lv": +6,  "Gv": +10},
            5:  {"V": +24, "I": -8,  "Lv": +15, "Gv": +35},
            10: {"V": +50, "I": -15, "Lv": +20, "Gv": +60},
        },
    },

    "endorphins": {
        "half_life":  6,
        "max_level":  10.0,
        "triggers":   ["run", "breathe", "walk", "food", "water"],
        "vital_triggers": [("energy", 2.0)],
        "levels": {
            1:  {"V": +5,  "I": -3,  "Lv": +8,  "Gv": +1},
            5:  {"V": +18, "I": -10, "Lv": +24, "Gv": +5},
            10: {"V": +35, "I": -18, "Lv": +40, "Gv": +10},
        },
    },

    "cortisol": {
        # Raises V slightly BUT also raises I —
        # "I must survive because something is wrong"
        "half_life":  8,
        "max_level":  10.0,
        "triggers":   ["danger", "threat", "ghost", "dark", "alone", "scared"],
        "vital_triggers": [("energy", 2.0), ("hunger", 2.0)],
        "levels": {
            1:  {"V": +4,  "I": +4,  "Lv": +6,  "Gv": +2},
            5:  {"V": +12, "I": +15, "Lv": +15, "Gv": +8},
            10: {"V": +20, "I": +35, "Lv": +28, "Gv": +15},
        },
    },

    "testosterona": {
        "half_life":  12,
        "max_level":  10.0,
        "triggers":   ["danger", "threat", "person", "alone"],
        "vital_triggers": [],
        "levels": {
            1:  {"V": +6,  "I": -1,  "Lv": +12, "Gv": +2},
            5:  {"V": +18, "I": -5,  "Lv": +30, "Gv": +8},
            10: {"V": +35, "I": -10, "Lv": +55, "Gv": +15},
        },
    },

    "noradrenaline": {
        # Raises V and also I slightly — active vigilance
        "half_life":  4,
        "max_level":  10.0,
        "triggers":   ["danger", "threat", "ghost", "shadow", "dark", "alone"],
        "vital_triggers": [],
        "levels": {
            1:  {"V": +5,  "I": +2,  "Lv": +8,  "Gv": +2},
            5:  {"V": +15, "I": +8,  "Lv": +22, "Gv": +6},
            10: {"V": +30, "I": +18, "Lv": +40, "Gv": +12},
        },
    },
}

# Precomputar decay factors
for _chem in CHEMICALS.values():
    _chem["decay_factor"] = 0.5 ** (1.0 / _chem["half_life"])

_ZERO_THRESHOLD = 0.05


# ── INTERPOLATION ─────────────────────────────────────────────────────────────

def _interpolate_push(levels_table, level):
    """
    Linearly interpolates the push vector given the circulating level.
      [0, 1]  → between zero and x1
      [1, 5]  → between x1 and x5
      [5, 10] → between x5 and x10
    """
    zero = {k: 0.0 for k in SOMATIC_KEYS}
    l1   = levels_table[1]
    l5   = levels_table[5]
    l10  = levels_table[10]

    if level <= 0:
        return zero
    elif level <= 1:
        t = level / 1.0
        return {k: zero[k] + t * (l1[k] - zero[k]) for k in SOMATIC_KEYS}
    elif level <= 5:
        t = (level - 1) / 4.0
        return {k: l1[k] + t * (l5[k] - l1[k]) for k in SOMATIC_KEYS}
    else:
        t = min((level - 5) / 5.0, 1.0)
        return {k: l5[k] + t * (l10[k] - l5[k]) for k in SOMATIC_KEYS}


# ── CHEMICAL SYSTEM ───────────────────────────────────────────────────────────

class ChemicalSystem:
    def __init__(self):
        self.levels = {name: 0.0 for name in CHEMICALS}

    # ── RELEASE ───────────────────────────────────────────────────────────────

    def release(self, chemical_name, amount=1.0):
        chem = CHEMICALS.get(chemical_name)
        if not chem:
            return
        self.levels[chemical_name] = min(
            chem["max_level"],
            self.levels[chemical_name] + amount
        )

    def process_triggers(self, active_concepts, vitality_stats=None):
        """
        Releases chemicals according to active concepts and critical needs.
        active_concepts : list[str]
        vitality_stats  : dict con need_name → {value, ...}
        """
        concept_set = set(active_concepts) if active_concepts else set()

        for chem_name, chem in CHEMICALS.items():
            # Concept triggers — 1 unit per event
            if concept_set & set(chem["triggers"]):
                self.release(chem_name, 1.0)

            # Vital triggers — scales according to depth below threshold
            if vitality_stats:
                for need_name, threshold in chem.get("vital_triggers", []):
                    need = vitality_stats.get(need_name)
                    if need is None:
                        continue
                    val = need.get("value", 10.0)
                    if val <= threshold:
                        depth = 1.0 - (val / threshold)
                        self.release(chem_name, depth * 0.5)

    # ── DECAY ─────────────────────────────────────────────────────────────────

    def decay(self):
        for name, chem in CHEMICALS.items():
            self.levels[name] *= chem["decay_factor"]
            if self.levels[name] < _ZERO_THRESHOLD:
                self.levels[name] = 0.0

    # ── PUSH ──────────────────────────────────────────────────────────────────

    def get_somatic_push(self):
        """
        Returns the combined somatic vector of all active chemicals.
        Each chemical interpolates its push based on its circulating level.
        """
        result = {k: 0.0 for k in SOMATIC_KEYS}
        for name, chem in CHEMICALS.items():
            level = self.levels[name]
            if level < _ZERO_THRESHOLD:
                continue
            push = _interpolate_push(chem["levels"], level)
            for k in SOMATIC_KEYS:
                result[k] += push[k]
        return result

    # ── STATUS ────────────────────────────────────────────────────────────────

    def status(self):
        out = {}
        for name, level in self.levels.items():
            if level >= _ZERO_THRESHOLD:
                chem = CHEMICALS[name]
                push = _interpolate_push(chem["levels"], level)
                out[name] = {
                    "level":      round(level, 3),
                    "max_level":  chem["max_level"],
                    "half_life":  chem["half_life"],
                    "push":       {k: round(v, 2) for k, v in push.items()},
                }
        return out

    def summary_line(self):
        parts = [f"{n}={v:.2f}" for n, v in self.levels.items() if v >= _ZERO_THRESHOLD]
        return " | ".join(parts) if parts else "all clear"
