# systems/response_system.py — CCM v4
# Automatic reflex responses triggered by D and C coherence values.
# These are NOT needs — they are instant internal reactions to the
# current coherence state, like physiological reflexes.
# Automatic physiological reflexes — triggered by D and C.

from db.db_somatic import SOMATIC_KEYS
from db.db_mental  import MENTAL_KEYS

INTERNAL_CATEGORIES = {

    # HIGH PULSE — threat detected
    "pulse_high": {
        "somatic":{"V": 150, "I": 170, "Lv": 180, "Gv": 10},
        "mental":{"P": 5, "A": 95, "Er": 90, "Rr": 5},
        "trigger": lambda D, C: D < -0.3,
    },

    # CRITICAL THREAT — maximum terror
    "threat_critical": {
        "somatic":{"V": 160, "I": 190, "Lv": 190, "Gv": 4},
        "mental":{"P": 2, "A": 98, "Er": 95, "Rr": 2},
        "trigger": lambda D, C: D < -0.5,
    },

    # STABILIZATION — system seeks coherence when near center
    "stability_push": {
        "somatic":{"V": 130, "I": 50, "Lv": 90, "Gv": 80},
        "mental":{"P": 70, "A": 20, "Er": 30, "Rr": 60},
        "trigger": lambda D, C: abs(D) < 0.05 and abs(C) < 0.05,
    },

    # RELIEF — lit room, person nearby, safety
    "relief": {
        "somatic":{"V": 180, "I": 20, "Lv": 30, "Gv": 160},
        "mental":{"P": 85, "A": 10, "Er": 15, "Rr": 80},
        "trigger": lambda D, C: D > 0.3 and C > 0.2,
    },

    # WITHDRAWAL — total collapse
    "withdrawal": {
        "somatic":{"V": 40, "I": 140, "Lv": 40, "Gv": 60},
        "mental":{"P": 20, "A": 70, "Er": 30, "Rr": 25},
        "trigger": lambda D, C: D < -0.4 and C < -0.3,
    },
}


def get_active_categories(D, C):
    return [(name, cat) for name, cat in INTERNAL_CATEGORIES.items()
            if cat["trigger"](D, C)]
