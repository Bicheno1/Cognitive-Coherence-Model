# motors/vitality_stats.py — CCM v5
#
# VITALITY STATS — active physiological statistics
#
# RECEIVES: inputs from the somatic external engine + elapsed time
# HACE:   actualiza y decays hunger, thirst, energy, temperature, commodity, health
# OUTPUTS: internal somatic pressure {V,I,Lv,Gv} + mental pressure {P,A,Er,Rr}
#
# Same as vital_system but renamed and cleaned up.
# Decay is autonomous — no inputs needed to decrease.

from systems.vital_system import VitalSystem as _VS

class VitalityStats:
    """Wrapper limpio sobre VitalSystem existente."""

    def __init__(self):
        self._vs = _VS()

    def tick(self, active_concepts: list = None):
        self._vs.tick(active_concepts=active_concepts or [])

    def push_commodity(self, delta: float):
        self._vs.push_commodity(delta)

    def get_pressure(self):
        """BOTA: (somatic_pressure, mental_pressure) — dicts {V,I,Lv,Gv} y {P,A,Er,Rr}"""
        return self._vs.get_internal_pressure()

    def status(self) -> dict:
        return self._vs.status()

    def get_need(self, name: str) -> dict:
        """Returns the stat of a specific need."""
        somatic = self._vs.somatic
        mental  = self._vs.mental
        return somatic.get(name) or mental.get(name) or {}

    def all_needs(self) -> dict:
        """Returns all needs as flat dict."""
        out = {}
        out.update(self._vs.somatic)
        out.update(self._vs.mental)
        return out

    def core_status(self) -> dict:
        """
        Returns: state in human language for each need.
        Ejemplo: {"energy": "cansado", "hunger": "hungry", ...}
        """
        needs = self.all_needs()
        result = {}
        for name, need in needs.items():
            val = need.get("value", 5.0)
            result[name] = _label(name, val)
        return result


# Ranges → state label  (somatic stats only)
_RANGES = {
    "hunger":      [(8, "full"),    (6, "satisfied"), (4, "hungry"),
                    (2, "hungry"), (0, "at limit")],
    "thirst":      [(8, "hydrated"),  (6, "ok"),         (4, "thirsty"),
                    (2, "very thirsty"),(0, "at limit")],
    "energy":      [(8, "descansado"), (6, "good"),       (4, "cansado"),
                    (2, "agotado"),    (0, "collapsed")],
    "temperature": [(8, "fresh"),     (6, "comfortable"),     (4, "hot"),
                    (2, "very hot"),(0, "critical")],
    "commodity":   [(8, "comfortable"),     (6, "ok"),         (4, "uncomfortable"),
                    (2, "very uncomfortable"),(0, "suffering")],
    "health":      [(8, "healthy"),       (6, "good"),       (4, "weak"),
                    (2, "sick"),    (0, "critical")],
}

def _label(name: str, value: float) -> str:
    ranges = _RANGES.get(name, [(5, "ok"), (0, "critical")])
    for threshold, label in ranges:
        if value >= threshold:
            return label
    return ranges[-1][1]
