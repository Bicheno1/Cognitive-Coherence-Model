# systems/core_system.py — CCM v5
#
# STAT_DATABASE — live record of the physical state of the host.
# CORE_RULES and identity functions live in motors/core_identity.py
#
# Updated by pre_input on each receptor event.
# Decays autonomously per tick (physical stats).
# Exposed to the cycle_manager as baseline pressure.
#
# Fields per stat:
#   value       : currently registered value
#   label       : last level de threshold (e.g. "elevado")
#   decay_rate  : deriva per tick hacia baseline
#   baseline    : value de reposo
#   source      : "receptor" | "event" | "cycle"
#   somatic     : last somatic vector from receptor lookup
#   mental      : last mental vector from receptor lookup

STAT_DATABASE = {

    # ── PHYSICAL — THERMORECEPTOR ─────────────────────────────────────────────
    "temperature_skin": {
        "value": 22.0, "label": "normal",
        "decay_rate": 0.5, "baseline": 22.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "temperature_core": {
        "value": 36.8, "label": "normal",
        "decay_rate": 0.05, "baseline": 36.8,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — NOCICEPTOR ─────────────────────────────────────────────────
    "pain": {
        "value": 0.0, "label": "muy_bajo",
        "decay_rate": 0.2, "baseline": 0.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "pain_visceral": {
        "value": 0.0, "label": "muy_bajo",
        "decay_rate": 0.1, "baseline": 0.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — MECHANORECEPTOR ────────────────────────────────────────────
    "pressure": {
        "value": 0.0, "label": "muy_bajo",
        "decay_rate": 1.0, "baseline": 0.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "vibration": {
        "value": 0.0, "label": "muy_bajo",
        "decay_rate": 2.0, "baseline": 0.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — PHOTORECEPTOR ──────────────────────────────────────────────
    "light_lux": {
        "value": 300.0, "label": "normal",
        "decay_rate": 10.0, "baseline": 300.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "light_wavelength": {
        "value": 530.0, "label": "green_neutral",
        "decay_rate": 0.0, "baseline": 530.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — AUDITORY ───────────────────────────────────────────────────
    "sound_db": {
        "value": 40.0, "label": "bajo",
        "decay_rate": 5.0, "baseline": 40.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "sound_hz": {
        "value": 1000.0, "label": "normal",
        "decay_rate": 0.0, "baseline": 1000.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — CHEMORECEPTOR OLFACTORY ───────────────────────────────────
    "smell_ppb": {
        "value": 0.0, "label": "muy_bajo",
        "decay_rate": 2.0, "baseline": 0.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — CHEMORECEPTOR TASTE ───────────────────────────────────────
    "taste_sweet":  {"value": 0.0,  "label": "muy_bajo", "decay_rate": 1.0, "baseline": 0.0, "source": "receptor", "somatic": None, "mental": None},
    "taste_bitter": {"value": 0.0,  "label": "muy_bajo", "decay_rate": 1.0, "baseline": 0.0, "source": "receptor", "somatic": None, "mental": None},
    "taste_salt":   {"value": 0.0,  "label": "muy_bajo", "decay_rate": 1.0, "baseline": 0.0, "source": "receptor", "somatic": None, "mental": None},
    "taste_acid":   {"value": 7.0,  "label": "normal",   "decay_rate": 1.0, "baseline": 7.0, "source": "receptor", "somatic": None, "mental": None},

    # ── PHYSICAL — INTERNAL O2 / CO2 ──────────────────────────────────────────
    "blood_o2": {
        "value": 98.0, "label": "normal",
        "decay_rate": 0.0, "baseline": 98.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "blood_co2": {
        "value": 40.0, "label": "normal",
        "decay_rate": 0.0, "baseline": 40.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — HUMIDITY ───────────────────────────────────────────────────
    "humidity": {
        "value": 50.0, "label": "normal",
        "decay_rate": 1.0, "baseline": 50.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — PROPRIOCEPTOR ──────────────────────────────────────────────
    "balance": {
        "value": 2.0, "label": "normal",
        "decay_rate": 0.5, "baseline": 2.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "muscle_tension": {
        "value": 20.0, "label": "bajo",
        "decay_rate": 1.0, "baseline": 20.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── PHYSICAL — INTEROCEPTOR ───────────────────────────────────────────────
    "heart_rate": {
        "value": 70.0, "label": "normal",
        "decay_rate": 0.5, "baseline": 70.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "breathing_rate": {
        "value": 15.0, "label": "normal",
        "decay_rate": 0.2, "baseline": 15.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "hunger": {
        "value": 1.0, "label": "muy_bajo",
        "decay_rate": -0.016,  # increases ~1h per real hour (negative = grows)
        "baseline": 0.0,
        "source": "receptor", "somatic": None, "mental": None,
    },
    "thirst": {
        "value": 0.0, "label": "muy_bajo",
        "decay_rate": -0.008,  # grows slower than hunger
        "baseline": 0.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── mental — COGNITIVE LOAD ───────────────────────────────────────────────
    "cognitive_load": {
        "value": 20.0, "label": "bajo",
        "decay_rate": 1.0, "baseline": 20.0,
        "source": "receptor", "somatic": None, "mental": None,
    },

    # ── mental — SOCIAL / EMOTIONAL (event-driven, slow decay) ───────────────
    "self_esteem": {
        "value": 0.7, "label": None,
        "decay_rate": 0.001, "baseline": 0.7,
        "source": "event", "somatic": None, "mental": None,
    },
    "security": {
        "value": 0.6, "label": None,
        "decay_rate": 0.002, "baseline": 0.6,
        "source": "event", "somatic": None, "mental": None,
    },
    "purpose": {
        "value": 0.6, "label": None,
        "decay_rate": 0.001, "baseline": 0.6,
        "source": "event", "somatic": None, "mental": None,
    },
    "company": {
        "value": 0.5, "label": None,
        "decay_rate": 0.002, "baseline": 0.5,
        "source": "event", "somatic": None, "mental": None,
    },
    "shame": {
        "value": 0.0, "label": None,
        "decay_rate": 0.005, "baseline": 0.0,
        "source": "event", "somatic": None, "mental": None,
    },
    "trust": {
        "value": 0.5, "label": None,
        "decay_rate": 0.001, "baseline": 0.5,
        "source": "event", "somatic": None, "mental": None,
    },

    # ── mental — CYCLE-DRIVEN (updated by cycle_manager) ─────────────────────
    "sanity": {
        "value": 0.9, "label": None,
        "decay_rate": 0.0005, "baseline": 1.0,
        "source": "cycle", "somatic": None, "mental": None,
    },
    "health": {
        "value": 0.9, "label": None,
        "decay_rate": 0.0002, "baseline": 1.0,
        "source": "cycle", "somatic": None, "mental": None,
    },
}


# ── STAT DATABASE API ──────────────────────────────────────────────────────────

def update_stat(stat_key: str, value: float, label: str = None,
                somatic: dict = None, mental: dict = None):
    """
    Called by pre_input after a receptor lookup.
    Updates value, label, and last vectors in STAT_DATABASE.
    """
    if stat_key not in STAT_DATABASE:
        return
    STAT_DATABASE[stat_key]["value"]   = value
    if label   is not None: STAT_DATABASE[stat_key]["label"]   = label
    if somatic is not None: STAT_DATABASE[stat_key]["somatic"] = somatic
    if mental  is not None: STAT_DATABASE[stat_key]["mental"]  = mental


def tick_decay(delta: float = 1.0):
    """
    Called each cycle tick. Decays physical stats toward baseline.
    delta = time elapsed (in seconds or abstract tick units).
    """
    for key, stat in STAT_DATABASE.items():
        rate = stat["decay_rate"]
        if rate == 0.0:
            continue
        current  = stat["value"]
        baseline = stat["baseline"]
        if rate > 0:
            # decay toward baseline (reduce distance)
            stat["value"] = current + (baseline - current) * min(rate * delta, 1.0)
        else:
            # grows autonomously (hunger, thirst)
            stat["value"] = current + abs(rate) * delta


def get_stat_pressure() -> dict:
    """
    Returns a summary of which stats are currently generating pressure
    (i.e. not at baseline / not at normal label).
    Used by cycle_manager as baseline offset.
    """
    pressure = {}
    for key, stat in STAT_DATABASE.items():
        somatic = stat.get("somatic")
        mental  = stat.get("mental")
        if somatic or mental:
            pressure[key] = {
                "label":   stat["label"],
                "somatic": somatic,
                "mental":  mental,
            }
    return pressure


def get_stat(key: str):
    """Returns a single stat entry."""
    return STAT_DATABASE.get(key)

