# motors/external_somatic.py — CCM v5
#
# SOMATIC EXTERNAL ENGINE
#
# RECEIVES: raw physical signals from the world
#   - rig properties (temperature, pressure, pain, posture)
#   - camera properties (objects with physical properties)
#
# DOES:
#   1. Classifies each signal by human receptor type
#   2. Scales by body zone (Penfield homunculus)
#   3. Vectorizes using db_receptors → {V, I, Lv, Gv}
#
# OUTPUTS: external somatic vector {V, I, Lv, Gv} + metadata

from db.db_receptors import lookup_receptor_weighted, lookup_receptor, RECEPTORS
from db.db_somatic import SOMATIC_KEYS, SOMATIC_MAX

_PROP_TO_RECEPTOR = {
    "temperature":      "temperature_skin",
    "temperature_skin": "temperature_skin",
    "temperature_core": "temperature_core",
    "pressure":         "pressure",
    "pain":             "pain",
    "pain_visceral":    "pain_visceral",
    "vibration":        "vibration",
    "light_lux":        "light_lux",
    "lux":              "light_lux",
    "sound_db":         "sound_db",
    "sound_hz":         "sound_hz",
    "smell_ppb":        "smell_ppb",
    "humidity":         "humidity",
    "heart_rate":       "heart_rate",
    "bpm":              "heart_rate",
    "breathing_rate":   "breathing_rate",
    "hunger":           "hunger",
    "thirst":           "thirst",
    "balance":          "balance",
    "muscle_tension":   "muscle_tension",
    "blood_o2":         "blood_o2",
    "blood_co2":        "blood_co2",
    "cognitive_load":   "cognitive_load",
}


def process(physical_inputs: list) -> dict | None:
    """
    RECIBE list of physical signals:
        [{"receptor": "temperature_skin", "value": 33.0, "zone": "face"}, ...]

    Returns averaged vector {V, I, Lv, Gv} from all activations,
    or None if no valid inputs.
    """
    vectors = []

    for inp in physical_inputs:
        receptor = inp.get("receptor")
        value    = inp.get("value")
        zone     = inp.get("zone")

        if receptor is None or value is None:
            continue

        match = (lookup_receptor_weighted(receptor, value, zone)
                 if zone else lookup_receptor(receptor, value))

        if not match:
            continue

        vectors.append({
            "somatic":  match["somatic"],
            "label":    match["label"],
            "receptor": receptor,
            "zone":     zone or "unspecified",
        })

    if not vectors:
        return None

    result = {k: 0.0 for k in SOMATIC_KEYS}
    for v in vectors:
        for k in SOMATIC_KEYS:
            result[k] += v["somatic"].get(k, 0.0)

    n = len(vectors)
    result = {k: min(SOMATIC_MAX, result[k] / n) for k in SOMATIC_KEYS}
    result["_pipeline"]    = "external_somatic"
    result["_activations"] = [{"receptor": v["receptor"],
                                "zone":     v["zone"],
                                "label":    v["label"]} for v in vectors]
    return result


def from_perception(scan: list) -> list:
    """
    Converts the output of perception_system.scan() into physical_inputs.
    Only properties that correspond to a known receptor are passed through.
    """
    known = set(RECEPTORS.keys())
    inputs = []
    for obj in scan:
        zone  = obj.get("properties", {}).get("zone") or obj.get("properties", {}).get("body_zone")
        for key, val in obj.get("properties", {}).items():
            rkey = _PROP_TO_RECEPTOR.get(key.lower())
            if rkey and rkey in known:
                try:
                    inputs.append({"receptor": rkey, "value": float(val), "zone": zone})
                except (ValueError, TypeError):
                    pass
    return inputs
