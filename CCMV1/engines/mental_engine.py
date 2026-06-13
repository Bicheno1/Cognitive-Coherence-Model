# engines/mental_engine.py
# mental engine — cognitive/emotional world — range 0-2
# Saturates earlier than somatic — mental overload is faster

from core.formulas import calculate_C, apply_input, get_quadrant, get_rhomboid_center, get_distance
from db.db_mental import MENTAL_KEYS, MENTAL_BASE
import math

class MentalEngine:
    def __init__(self):
        self.base     = dict(MENTAL_BASE)
        self.current  = dict(MENTAL_BASE)
        self.internal = {k: 0.0 for k in MENTAL_KEYS}
        self.external = dict(MENTAL_BASE)

    def apply_external(self, input_values):
        base_input   = apply_input(self.base, input_values, MENTAL_KEYS)
        self.current = apply_input(self.current, base_input, MENTAL_KEYS)
        self.external = dict(self.current)

    def apply_internal(self, internal_values):
        self.current  = apply_input(self.current, internal_values, MENTAL_KEYS)
        self.internal = dict(internal_values)

    def recalibrate(self, D):
        """Cross-recalibration — somatic coherence influences mental state.
        D is (cx, cy) of the somatic center of mass.
        cy > 0 → viable  → raises P, lowers A
        cy < 0 → inviable → lowers P, raises A
        """
        cx, cy = D
        influence = math.sqrt(cx**2 + cy**2) * 0.1
        sign = 1 if cy >= 0 else -1
        self.current["P"] = max(0.0, min(200.0, self.current["P"] + influence * sign))
        self.current["A"] = max(0.0, min(200.0, self.current["A"] - influence * sign))

    def current_state(self):
        return dict(self.current)

    def C(self):
        return calculate_C(self.current)

    def distance(self):
        return get_distance(self.current, MENTAL_KEYS)

    def quadrant(self):
        return get_quadrant(self.current, MENTAL_KEYS)

    def decay_toward_base(self, rate: float = 0.15):
        """
        Homeostatic decay — pushes current toward base each cycle.
        """
        for k in ["P", "A", "Er", "Rr"]:
            diff = self.base[k] - self.current[k]
            self.current[k] += diff * rate
