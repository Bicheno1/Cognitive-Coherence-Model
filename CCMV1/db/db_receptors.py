# db/db_receptors.py — CCM v5
#
# receptor database — physical properties → CCM vectors.
# Thresholds from CCM_Umbrales.xlsx | Zone weights from CCM_Homunculus.xlsx
#
# LEVELS (very_low → saturated):
#   very_low  — below functional threshold (deficit / deprivation)
#   low       — suboptimal tolerable (mild signal)
#   normal    — optimal zone (homeostasis)
#   high      — above optimal (stress / alert)
#   saturated — collapse threshold (damage / loss of consciousness)
#
# Each level has:
#   range   : (min, max) — None = open end
#   somatic : {V, I, Lv, Gv}
#   mental  : {P, A, Er, Rr}

# ── HOMUNCULUS DENSITY WEIGHTS ─────────────────────────────────────────────────
# Source: Penfield & Rasmussen (1950), McGlone et al. (2014)
# Scale 1–10 per receptor family per body zone
HOMUNCULUS = {
    "lips":            {"thermo":9,"touch":10,"vibr":8,"pain":7,"photo":0,"chemo":8,"proprio":4,"intero":0},
    "tongue":          {"thermo":8,"touch":10,"vibr":7,"pain":7,"photo":0,"chemo":10,"proprio":3,"intero":5},
    "fingertips":      {"thermo":8,"touch":10,"vibr":10,"pain":7,"photo":0,"chemo":3,"proprio":6,"intero":0},
    "palm":            {"thermo":7,"touch":9,"vibr":9,"pain":6,"photo":0,"chemo":3,"proprio":7,"intero":0},
    "hand_dorsum":     {"thermo":6,"touch":7,"vibr":7,"pain":6,"photo":0,"chemo":2,"proprio":5,"intero":0},
    "face":            {"thermo":8,"touch":8,"vibr":6,"pain":6,"photo":0,"chemo":4,"proprio":3,"intero":0},
    "forehead":        {"thermo":7,"touch":7,"vibr":5,"pain":5,"photo":0,"chemo":3,"proprio":2,"intero":0},
    "scalp":           {"thermo":5,"touch":6,"vibr":4,"pain":5,"photo":0,"chemo":2,"proprio":2,"intero":0},
    "neck_anterior":   {"thermo":7,"touch":7,"vibr":5,"pain":7,"photo":0,"chemo":3,"proprio":3,"intero":5},
    "chest":           {"thermo":6,"touch":6,"vibr":5,"pain":6,"photo":0,"chemo":2,"proprio":3,"intero":8},
    "abdomen":         {"thermo":6,"touch":5,"vibr":4,"pain":7,"photo":0,"chemo":2,"proprio":3,"intero":9},
    "genitals":        {"thermo":9,"touch":10,"vibr":8,"pain":8,"photo":0,"chemo":5,"proprio":4,"intero":7},
    "perineal":        {"thermo":7,"touch":8,"vibr":6,"pain":8,"photo":0,"chemo":4,"proprio":4,"intero":8},
    "foot_sole":       {"thermo":7,"touch":8,"vibr":8,"pain":6,"photo":0,"chemo":2,"proprio":9,"intero":0},
    "toes":            {"thermo":6,"touch":7,"vibr":6,"pain":6,"photo":0,"chemo":2,"proprio":8,"intero":0},
    "calf":            {"thermo":4,"touch":4,"vibr":4,"pain":5,"photo":0,"chemo":1,"proprio":8,"intero":2},
    "thigh":           {"thermo":4,"touch":4,"vibr":4,"pain":5,"photo":0,"chemo":1,"proprio":7,"intero":2},
    "lower_back":      {"thermo":5,"touch":4,"vibr":3,"pain":7,"photo":0,"chemo":1,"proprio":6,"intero":4},
    "upper_back":      {"thermo":5,"touch":4,"vibr":3,"pain":6,"photo":0,"chemo":1,"proprio":5,"intero":3},
    "shoulder":        {"thermo":5,"touch":5,"vibr":4,"pain":6,"photo":0,"chemo":1,"proprio":7,"intero":3},
    "arm":             {"thermo":5,"touch":5,"vibr":4,"pain":5,"photo":0,"chemo":1,"proprio":7,"intero":2},
    "forearm":         {"thermo":6,"touch":6,"vibr":5,"pain":5,"photo":0,"chemo":2,"proprio":6,"intero":2},
    "armpit":          {"thermo":7,"touch":6,"vibr":4,"pain":5,"photo":0,"chemo":5,"proprio":3,"intero":2},
    "ear_external":    {"thermo":6,"touch":5,"vibr":3,"pain":5,"photo":10,"chemo":3,"proprio":2,"intero":0},
    "eye_retina":      {"thermo":4,"touch":3,"vibr":2,"pain":4,"photo":10,"chemo":2,"proprio":1,"intero":0},
    "nose_mucosa":     {"thermo":7,"touch":5,"vibr":3,"pain":5,"photo":0,"chemo":10,"proprio":2,"intero":2},
    "lungs":           {"thermo":4,"touch":3,"vibr":2,"pain":5,"photo":0,"chemo":6,"proprio":3,"intero":10},
    "stomach":         {"thermo":4,"touch":3,"vibr":2,"pain":7,"photo":0,"chemo":7,"proprio":3,"intero":10},
    "intestine":       {"thermo":3,"touch":2,"vibr":1,"pain":6,"photo":0,"chemo":7,"proprio":2,"intero":10},
    "bladder_kidney":  {"thermo":3,"touch":2,"vibr":1,"pain":7,"photo":0,"chemo":4,"proprio":2,"intero":10},
    "heart_vessels":   {"thermo":3,"touch":2,"vibr":1,"pain":6,"photo":0,"chemo":5,"proprio":2,"intero":10},
    "muscles_general": {"thermo":4,"touch":3,"vibr":3,"pain":6,"photo":0,"chemo":1,"proprio":10,"intero":4},
    "tendons_joints":  {"thermo":4,"touch":3,"vibr":3,"pain":6,"photo":0,"chemo":1,"proprio":10,"intero":3},
    "vestibular":      {"thermo":3,"touch":2,"vibr":2,"pain":2,"photo":8,"chemo":1,"proprio":10,"intero":2},
}


def get_zone_weight(zone: str, family: str) -> float:
    """Normalized density weight (0.0–1.0) for a zone+receptor family."""
    zone_data = HOMUNCULUS.get(zone)
    if not zone_data:
        return 0.5
    return zone_data.get(family, 5) / 10.0


# ── receptor DATABASE ──────────────────────────────────────────────────────────
RECEPTORS = {

    # ── TERMORRECEPTOR ────────────────────────────────────────────────────────
    "temperature_skin": {
        "unit": "°C", "stat": "temperature_skin", "family": "thermo",
        "levels": [
            {"label":"muy_bajo", "range":(None,0),   "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 90,"Rr": 10}},
            {"label":"bajo",     "range":(0,18),     "somatic":{"V": 80,"I": 100,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 60,"Er": 50,"Rr": 40}},
            {"label":"normal",   "range":(18,26),    "somatic":{"V": 200,"I": 0,"Lv": 180,"Gv": 60}, "mental":{"P": 90,"A": 0,"Er": 10,"Rr": 90}},
            {"label":"elevado",  "range":(26,40),    "somatic":{"V": 80,"I": 100,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 60,"Er": 50,"Rr": 40}},
            {"label":"saturated", "range":(40,None),  "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 90,"Rr": 0}},
        ],
    },

    "temperature_core": {
        "unit": "°C", "stat": "temperature_core", "family": "intero",
        "levels": [
            {"label":"muy_bajo", "range":(None,35),  "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 100,"Rr": 0}},
            {"label":"bajo",     "range":(35,36),    "somatic":{"V": 80,"I": 100,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 60,"Er": 60,"Rr": 30}},
            {"label":"normal",   "range":(36,37.5),  "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 60}, "mental":{"P": 100,"A": 0,"Er": 0,"Rr": 100}},
            {"label":"elevado",  "range":(37.5,39),  "somatic":{"V": 80,"I": 100,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 60,"Er": 50,"Rr": 40}},
            {"label":"saturated", "range":(39,None),  "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 90,"Rr": 10}},
        ],
    },

    # ── NOCICEPTOR ────────────────────────────────────────────────────────────
    "pain": {
        "unit": "EVA 0–10", "stat": "pain", "family": "pain",
        "levels": [
            {"label":"muy_bajo", "range":(0,1),     "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 60}, "mental":{"P": 100,"A": 0,"Er": 0,"Rr": 100}},
            {"label":"bajo",     "range":(1,4),     "somatic":{"V": 140,"I": 40,"Lv": 140,"Gv": 40}, "mental":{"P": 70,"A": 20,"Er": 30,"Rr": 60}},
            {"label":"normal",   "range":(4,7),     "somatic":{"V": 60,"I": 120,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 70,"Er": 70,"Rr": 30}},
            {"label":"elevado",  "range":(7,9),     "somatic":{"V": 20,"I": 180,"Lv": 20,"Gv": 40}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 10}},
            {"label":"saturated", "range":(9,None),  "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 100,"Rr": 0}},
        ],
    },

    "pain_visceral": {
        "unit": "EVA 0–10", "stat": "pain_visceral", "family": "pain",
        "levels": [
            {"label":"muy_bajo", "range":(0,1),     "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 60}, "mental":{"P": 100,"A": 0,"Er": 0,"Rr": 100}},
            {"label":"bajo",     "range":(1,4),     "somatic":{"V": 140,"I": 40,"Lv": 140,"Gv": 40}, "mental":{"P": 70,"A": 20,"Er": 30,"Rr": 60}},
            {"label":"saturated", "range":(4,None),  "somatic":{"V": 20,"I": 180,"Lv": 20,"Gv": 40}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 10}},
        ],
    },

    # ── MECHANORECEPTOR — PRESSURE / TOUCH ─────────────────────────────────────
    "pressure": {
        "unit": "kPa", "stat": "pressure", "family": "touch",
        "levels": [
            {"label":"muy_bajo", "range":(0,0.1),   "somatic":{"V": 100,"I": 20,"Lv": 80,"Gv": 40}, "mental":{"P": 50,"A": 20,"Er": 10,"Rr": 70}},
            {"label":"bajo",     "range":(0.1,1),   "somatic":{"V": 160,"I": 0,"Lv": 160,"Gv": 80}, "mental":{"P": 80,"A": 0,"Er": 50,"Rr": 40}},
            {"label":"normal",   "range":(1,10),    "somatic":{"V": 140,"I": 20,"Lv": 140,"Gv": 60}, "mental":{"P": 70,"A": 10,"Er": 30,"Rr": 60}},
            {"label":"elevado",  "range":(10,50),   "somatic":{"V": 60,"I": 100,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 60,"Er": 60,"Rr": 30}},
            {"label":"saturated", "range":(50,None), "somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 10}},
        ],
    },

    # ── MECHANORECEPTOR — VIBRATION ───────────────────────────────────────────
    "vibration": {
        "unit": "Hz", "stat": "vibration", "family": "vibr",
        "levels": [
            {"label":"muy_bajo", "range":(0,20),    "somatic":{"V": 100,"I": 0,"Lv": 80,"Gv": 40}, "mental":{"P": 60,"A": 10,"Er": 10,"Rr": 80}},
            {"label":"bajo",     "range":(20,80),   "somatic":{"V": 120,"I": 20,"Lv": 120,"Gv": 60}, "mental":{"P": 60,"A": 10,"Er": 40,"Rr": 50}},
            {"label":"normal",   "range":(80,200),  "somatic":{"V": 100,"I": 40,"Lv": 100,"Gv": 40}, "mental":{"P": 40,"A": 30,"Er": 50,"Rr": 40}},
            {"label":"elevado",  "range":(200,300), "somatic":{"V": 60,"I": 80,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 60,"Er": 60,"Rr": 30}},
            {"label":"saturated", "range":(300,None),"somatic":{"V": 0,"I": 160,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 80,"Er": 80,"Rr": 10}},
        ],
    },

    # ── FOTORRECEPTOR — LUMINOSIDAD ───────────────────────────────────────────
    "light_lux": {
        "unit": "lux", "stat": "light_lux", "family": "photo",
        "levels": [
            {"label":"muy_bajo", "range":(0,1),       "somatic":{"V": 40,"I": 120,"Lv": 40,"Gv": 40}, "mental":{"P": 10,"A": 80,"Er": 60,"Rr": 20}},
            {"label":"bajo",     "range":(1,100),     "somatic":{"V": 100,"I": 40,"Lv": 100,"Gv": 40}, "mental":{"P": 50,"A": 30,"Er": 30,"Rr": 60}},
            {"label":"normal",   "range":(100,1000),  "somatic":{"V": 180,"I": 0,"Lv": 160,"Gv": 60}, "mental":{"P": 90,"A": 0,"Er": 20,"Rr": 80}},
            {"label":"elevado",  "range":(1000,50000),"somatic":{"V": 100,"I": 60,"Lv": 100,"Gv": 60}, "mental":{"P": 40,"A": 40,"Er": 40,"Rr": 50}},
            {"label":"saturated", "range":(50000,None),"somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 90,"Er": 80,"Rr": 10}},
        ],
    },

    "light_wavelength": {
        "unit": "nm", "stat": "light_wavelength", "family": "photo",
        "levels": [
            {"label":"infrared",      "range":(700,None), "somatic":{"V": 100,"I": 40,"Lv": 100,"Gv": 40}, "mental":{"P": 50,"A": 30,"Er": 30,"Rr": 50}},
            {"label":"red",           "range":(620,700),  "somatic":{"V": 100,"I": 60,"Lv": 100,"Gv": 60}, "mental":{"P": 40,"A": 40,"Er": 60,"Rr": 40}},
            {"label":"yellow_orange", "range":(570,620),  "somatic":{"V": 120,"I": 40,"Lv": 120,"Gv": 60}, "mental":{"P": 50,"A": 30,"Er": 50,"Rr": 40}},
            {"label":"green_neutral", "range":(495,570),  "somatic":{"V": 140,"I": 0,"Lv": 120,"Gv": 80}, "mental":{"P": 70,"A": 10,"Er": 30,"Rr": 70}},
            {"label":"blue_calm",     "range":(450,495),  "somatic":{"V": 120,"I": 20,"Lv": 120,"Gv": 80}, "mental":{"P": 70,"A": 10,"Er": 30,"Rr": 70}},
            {"label":"violet",        "range":(380,450),  "somatic":{"V": 100,"I": 40,"Lv": 100,"Gv": 60}, "mental":{"P": 50,"A": 30,"Er": 40,"Rr": 50}},
            {"label":"ultraviolet",   "range":(None,380), "somatic":{"V": 60,"I": 100,"Lv": 60,"Gv": 40}, "mental":{"P": 30,"A": 50,"Er": 40,"Rr": 40}},
        ],
    },

    # ── MECANORRECEPTOR AUDITIVO — VOLUMEN ────────────────────────────────────
    "sound_db": {
        "unit": "dB", "stat": "sound_db", "family": "photo",
        "levels": [
            {"label":"muy_bajo", "range":(0,20),    "somatic":{"V": 120,"I": 0,"Lv": 100,"Gv": 40}, "mental":{"P": 60,"A": 20,"Er": 20,"Rr": 80}},
            {"label":"bajo",     "range":(20,50),   "somatic":{"V": 140,"I": 0,"Lv": 120,"Gv": 60}, "mental":{"P": 70,"A": 10,"Er": 30,"Rr": 60}},
            {"label":"normal",   "range":(50,70),   "somatic":{"V": 160,"I": 0,"Lv": 140,"Gv": 100}, "mental":{"P": 80,"A": 10,"Er": 40,"Rr": 60}},
            {"label":"elevado",  "range":(70,90),   "somatic":{"V": 60,"I": 80,"Lv": 60,"Gv": 60}, "mental":{"P": 20,"A": 60,"Er": 60,"Rr": 30}},
            {"label":"saturated", "range":(90,None), "somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 0}},
        ],
    },

    "sound_hz": {
        "unit": "Hz", "stat": "sound_hz", "family": "photo",
        "levels": [
            {"label":"muy_bajo", "range":(None,20),   "somatic":{"V": 60,"I": 80,"Lv": 60,"Gv": 40}, "mental":{"P": 30,"A": 50,"Er": 50,"Rr": 30}},
            {"label":"bajo",     "range":(20,300),    "somatic":{"V": 120,"I": 0,"Lv": 120,"Gv": 80}, "mental":{"P": 60,"A": 10,"Er": 50,"Rr": 40}},
            {"label":"normal",   "range":(300,3000),  "somatic":{"V": 160,"I": 0,"Lv": 140,"Gv": 100}, "mental":{"P": 80,"A": 10,"Er": 50,"Rr": 60}},
            {"label":"elevado",  "range":(3000,8000), "somatic":{"V": 60,"I": 80,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 60,"Er": 60,"Rr": 30}},
            {"label":"saturated", "range":(8000,None), "somatic":{"V": 0,"I": 160,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 80,"Er": 80,"Rr": 10}},
        ],
    },

    # ── CHEMORECEPTOR — SMELL ────────────────────────────────────────────────
    "smell_ppb": {
        "unit": "ppb", "stat": "smell_ppb", "family": "chemo",
        "levels": [
            {"label":"muy_bajo", "range":(0,1),     "somatic":{"V": 120,"I": 0,"Lv": 100,"Gv": 40}, "mental":{"P": 70,"A": 10,"Er": 10,"Rr": 80}},
            {"label":"bajo",     "range":(1,10),    "somatic":{"V": 140,"I": 0,"Lv": 140,"Gv": 80}, "mental":{"P": 70,"A": 0,"Er": 50,"Rr": 40}},
            {"label":"normal",   "range":(10,100),  "somatic":{"V": 100,"I": 20,"Lv": 100,"Gv": 40}, "mental":{"P": 50,"A": 10,"Er": 30,"Rr": 60}},
            {"label":"elevado",  "range":(100,500), "somatic":{"V": 40,"I": 100,"Lv": 40,"Gv": 40}, "mental":{"P": 20,"A": 60,"Er": 60,"Rr": 30}},
            {"label":"saturated", "range":(500,None),"somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 40}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 10}},
        ],
    },

    # ── QUIMIORRECEPTOR — GUSTO ───────────────────────────────────────────────
    "taste_sweet": {
        "unit": "% concentration", "stat": "taste_sweet", "family": "chemo",
        "levels": [
            {"label":"muy_bajo", "range":(0,0.5),   "somatic":{"V": 100,"I": 0,"Lv": 100,"Gv": 40}, "mental":{"P": 50,"A": 10,"Er": 10,"Rr": 70}},
            {"label":"bajo",     "range":(0.5,2),   "somatic":{"V": 160,"I": 0,"Lv": 160,"Gv": 60}, "mental":{"P": 70,"A": 0,"Er": 50,"Rr": 40}},
            {"label":"normal",   "range":(2,5),     "somatic":{"V": 180,"I": 0,"Lv": 180,"Gv": 60}, "mental":{"P": 80,"A": 0,"Er": 50,"Rr": 50}},
            {"label":"elevado",  "range":(5,10),    "somatic":{"V": 80,"I": 60,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 40,"Er": 40,"Rr": 40}},
            {"label":"saturated", "range":(10,None), "somatic":{"V": 20,"I": 140,"Lv": 20,"Gv": 40}, "mental":{"P": 10,"A": 70,"Er": 70,"Rr": 20}},
        ],
    },

    "taste_bitter": {
        "unit": "threshold 0–1", "stat": "taste_bitter", "family": "chemo",
        "levels": [
            {"label":"muy_bajo", "range":(0,0.1),    "somatic":{"V": 100,"I": 0,"Lv": 100,"Gv": 40}, "mental":{"P": 50,"A": 10,"Er": 10,"Rr": 70}},
            {"label":"bajo",     "range":(0.1,0.3),  "somatic":{"V": 100,"I": 40,"Lv": 100,"Gv": 40}, "mental":{"P": 40,"A": 30,"Er": 40,"Rr": 50}},
            {"label":"normal",   "range":(0.3,0.6),  "somatic":{"V": 60,"I": 80,"Lv": 60,"Gv": 40}, "mental":{"P": 30,"A": 50,"Er": 50,"Rr": 40}},
            {"label":"elevado",  "range":(0.6,0.85), "somatic":{"V": 20,"I": 140,"Lv": 20,"Gv": 40}, "mental":{"P": 10,"A": 70,"Er": 70,"Rr": 20}},
            {"label":"saturated", "range":(0.85,None),"somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 40}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 10}},
        ],
    },

    "taste_salt": {
        "unit": "% NaCl", "stat": "taste_salt", "family": "chemo",
        "levels": [
            {"label":"muy_bajo", "range":(0,0.2),   "somatic":{"V": 100,"I": 20,"Lv": 100,"Gv": 40}, "mental":{"P": 50,"A": 20,"Er": 20,"Rr": 60}},
            {"label":"normal",   "range":(0.5,1),   "somatic":{"V": 160,"I": 0,"Lv": 160,"Gv": 60}, "mental":{"P": 70,"A": 0,"Er": 30,"Rr": 60}},
            {"label":"elevado",  "range":(1,2),     "somatic":{"V": 80,"I": 60,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 40,"Er": 40,"Rr": 40}},
            {"label":"saturated", "range":(2,None),  "somatic":{"V": 40,"I": 100,"Lv": 40,"Gv": 40}, "mental":{"P": 20,"A": 50,"Er": 50,"Rr": 30}},
        ],
    },

    "taste_acid": {
        "unit": "pH", "stat": "taste_acid", "family": "chemo",
        "levels": [
            {"label":"saturated", "range":(None,3),  "somatic":{"V": 20,"I": 140,"Lv": 20,"Gv": 40}, "mental":{"P": 10,"A": 70,"Er": 70,"Rr": 20}},
            {"label":"elevado",  "range":(3,5),     "somatic":{"V": 80,"I": 60,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 40,"Er": 50,"Rr": 40}},
            {"label":"normal",   "range":(5,7.5),   "somatic":{"V": 160,"I": 0,"Lv": 160,"Gv": 60}, "mental":{"P": 70,"A": 0,"Er": 20,"Rr": 70}},
            {"label":"bajo",     "range":(7.5,9),   "somatic":{"V": 100,"I": 40,"Lv": 100,"Gv": 40}, "mental":{"P": 40,"A": 30,"Er": 30,"Rr": 50}},
        ],
    },

    # ── QUIMIORRECEPTOR — O2 / CO2 ────────────────────────────────────────────
    "blood_o2": {
        "unit": "% SpO2", "stat": "blood_o2", "family": "chemo",
        "levels": [
            {"label":"muy_bajo", "range":(None,85), "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 100,"Rr": 0}},
            {"label":"bajo",     "range":(85,95),   "somatic":{"V": 40,"I": 140,"Lv": 40,"Gv": 40}, "mental":{"P": 10,"A": 80,"Er": 70,"Rr": 20}},
            {"label":"normal",   "range":(95,None), "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 60}, "mental":{"P": 100,"A": 0,"Er": 0,"Rr": 100}},
        ],
    },

    "blood_co2": {
        "unit": "mmHg", "stat": "blood_co2", "family": "chemo",
        "levels": [
            {"label":"normal",   "range":(35,45),   "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 40}, "mental":{"P": 100,"A": 0,"Er": 0,"Rr": 100}},
            {"label":"elevado",  "range":(45,None), "somatic":{"V": 20,"I": 160,"Lv": 20,"Gv": 40}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 10}},
        ],
    },

    # ── QUIMIORRECEPTOR — HUMEDAD ─────────────────────────────────────────────
    "humidity": {
        "unit": "% HR", "stat": "humidity", "family": "chemo",
        "levels": [
            {"label":"muy_bajo", "range":(None,20), "somatic":{"V": 60,"I": 100,"Lv": 60,"Gv": 40}, "mental":{"P": 30,"A": 50,"Er": 30,"Rr": 50}},
            {"label":"bajo",     "range":(20,40),   "somatic":{"V": 120,"I": 40,"Lv": 120,"Gv": 40}, "mental":{"P": 60,"A": 20,"Er": 20,"Rr": 60}},
            {"label":"normal",   "range":(40,60),   "somatic":{"V": 200,"I": 0,"Lv": 180,"Gv": 60}, "mental":{"P": 90,"A": 0,"Er": 10,"Rr": 90}},
            {"label":"elevado",  "range":(60,80),   "somatic":{"V": 100,"I": 60,"Lv": 100,"Gv": 40}, "mental":{"P": 40,"A": 40,"Er": 30,"Rr": 50}},
            {"label":"saturated", "range":(80,None), "somatic":{"V": 40,"I": 120,"Lv": 40,"Gv": 40}, "mental":{"P": 20,"A": 60,"Er": 50,"Rr": 30}},
        ],
    },

    # ── PROPRIOCEPTOR — BALANCE ──────────────────────────────────────────────
    # 0=freefall  1=unstable  2=stable  3=acceleration  4=vertigo
    "balance": {
        "unit": "state 0–4", "stat": "balance", "family": "proprio",
        "levels": [
            {"label":"muy_bajo", "range":(0,0.5),   "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 100,"Rr": 0}},
            {"label":"bajo",     "range":(0.5,1.5), "somatic":{"V": 60,"I": 100,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 70,"Er": 60,"Rr": 30}},
            {"label":"normal",   "range":(1.5,2.5), "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 40}, "mental":{"P": 100,"A": 0,"Er": 10,"Rr": 90}},
            {"label":"elevado",  "range":(2.5,3.5), "somatic":{"V": 60,"I": 100,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 70,"Er": 70,"Rr": 20}},
            {"label":"saturated", "range":(3.5,None),"somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 0}},
        ],
    },

    # ── PROPRIOCEPTOR — MUSCLE tension ──────────────────────────────────────
    "muscle_tension": {
        "unit": "% MVC", "stat": "muscle_tension", "family": "proprio",
        "levels": [
            {"label":"muy_bajo", "range":(0,10),    "somatic":{"V": 40,"I": 120,"Lv": 40,"Gv": 20}, "mental":{"P": 30,"A": 60,"Er": 40,"Rr": 40}},
            {"label":"bajo",     "range":(10,30),   "somatic":{"V": 160,"I": 0,"Lv": 160,"Gv": 40}, "mental":{"P": 80,"A": 0,"Er": 10,"Rr": 90}},
            {"label":"normal",   "range":(30,60),   "somatic":{"V": 180,"I": 0,"Lv": 180,"Gv": 40}, "mental":{"P": 80,"A": 0,"Er": 20,"Rr": 70}},
            {"label":"elevado",  "range":(60,80),   "somatic":{"V": 80,"I": 80,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 50,"Er": 50,"Rr": 40}},
            {"label":"saturated", "range":(80,None), "somatic":{"V": 0,"I": 160,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 80,"Er": 80,"Rr": 10}},
        ],
    },

    # ── INTEROCEPTOR — HEART ────────────────────────────────────────────────
    "heart_rate": {
        "unit": "bpm", "stat": "heart_rate", "family": "intero",
        "levels": [
            {"label":"muy_bajo", "range":(None,40),  "somatic":{"V": 20,"I": 180,"Lv": 20,"Gv": 20}, "mental":{"P": 10,"A": 90,"Er": 80,"Rr": 10}},
            {"label":"bajo",     "range":(40,60),    "somatic":{"V": 140,"I": 20,"Lv": 140,"Gv": 40}, "mental":{"P": 70,"A": 10,"Er": 20,"Rr": 70}},
            {"label":"normal",   "range":(60,100),   "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 40}, "mental":{"P": 100,"A": 0,"Er": 0,"Rr": 100}},
            {"label":"elevado",  "range":(100,140),  "somatic":{"V": 80,"I": 80,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 60,"Er": 60,"Rr": 30}},
            {"label":"saturated", "range":(140,None), "somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 0}},
        ],
    },

    # ── INTEROCEPTOR — BREATHING ────────────────────────────────────────────
    "breathing_rate": {
        "unit": "rpm", "stat": "breathing_rate", "family": "intero",
        "levels": [
            {"label":"muy_bajo", "range":(None,8),  "somatic":{"V": 20,"I": 180,"Lv": 20,"Gv": 20}, "mental":{"P": 10,"A": 90,"Er": 70,"Rr": 10}},
            {"label":"bajo",     "range":(8,12),    "somatic":{"V": 160,"I": 0,"Lv": 160,"Gv": 40}, "mental":{"P": 90,"A": 0,"Er": 20,"Rr": 80}},
            {"label":"normal",   "range":(12,20),   "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 40}, "mental":{"P": 100,"A": 0,"Er": 0,"Rr": 100}},
            {"label":"elevado",  "range":(20,30),   "somatic":{"V": 60,"I": 100,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 70,"Er": 70,"Rr": 20}},
            {"label":"saturated", "range":(30,None), "somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 0}},
        ],
    },

    # ── INTEROCEPTOR — HAMBRE ────────────────────────────────────────────────
    "hunger": {
        "unit": "hours without eating", "stat": "hunger", "family": "intero",
        "levels": [
            {"label":"muy_bajo", "range":(0,2),     "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 40}, "mental":{"P": 90,"A": 0,"Er": 10,"Rr": 80}},
            {"label":"bajo",     "range":(2,4),     "somatic":{"V": 140,"I": 20,"Lv": 140,"Gv": 40}, "mental":{"P": 60,"A": 20,"Er": 20,"Rr": 70}},
            {"label":"normal",   "range":(4,8),     "somatic":{"V": 80,"I": 80,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 50,"Er": 50,"Rr": 40}},
            {"label":"elevado",  "range":(8,24),    "somatic":{"V": 20,"I": 160,"Lv": 20,"Gv": 20}, "mental":{"P": 10,"A": 80,"Er": 80,"Rr": 20}},
            {"label":"saturated", "range":(24,None), "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 90,"Rr": 0}},
        ],
    },

    # ── INTEROCEPTOR — SED ────────────────────────────────────────────────────
    "thirst": {
        "unit": "% dehydration", "stat": "thirst", "family": "intero",
        "levels": [
            {"label":"muy_bajo", "range":(0,0.5),   "somatic":{"V": 200,"I": 0,"Lv": 200,"Gv": 40}, "mental":{"P": 90,"A": 0,"Er": 0,"Rr": 100}},
            {"label":"bajo",     "range":(0.5,1),   "somatic":{"V": 140,"I": 20,"Lv": 140,"Gv": 40}, "mental":{"P": 60,"A": 20,"Er": 20,"Rr": 70}},
            {"label":"normal",   "range":(1,3),     "somatic":{"V": 80,"I": 80,"Lv": 80,"Gv": 40}, "mental":{"P": 30,"A": 50,"Er": 50,"Rr": 40}},
            {"label":"elevado",  "range":(3,6),     "somatic":{"V": 20,"I": 160,"Lv": 20,"Gv": 20}, "mental":{"P": 10,"A": 80,"Er": 70,"Rr": 20}},
            {"label":"saturated", "range":(6,None),  "somatic":{"V": 0,"I": 200,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 100,"Er": 90,"Rr": 0}},
        ],
    },

    # ── CARGA COGNITIVA ───────────────────────────────────────────────────────
    "cognitive_load": {
        "unit": "% capacity", "stat": "cognitive_load", "family": "intero",
        "levels": [
            {"label":"muy_bajo", "range":(0,10),    "somatic":{"V": 100,"I": 20,"Lv": 100,"Gv": 40}, "mental":{"P": 60,"A": 20,"Er": 20,"Rr": 70}},
            {"label":"bajo",     "range":(10,30),   "somatic":{"V": 180,"I": 0,"Lv": 180,"Gv": 60}, "mental":{"P": 90,"A": 0,"Er": 30,"Rr": 90}},
            {"label":"normal",   "range":(30,60),   "somatic":{"V": 140,"I": 20,"Lv": 140,"Gv": 60}, "mental":{"P": 70,"A": 20,"Er": 50,"Rr": 70}},
            {"label":"elevado",  "range":(60,80),   "somatic":{"V": 60,"I": 100,"Lv": 60,"Gv": 40}, "mental":{"P": 20,"A": 70,"Er": 70,"Rr": 20}},
            {"label":"saturated", "range":(80,None), "somatic":{"V": 0,"I": 180,"Lv": 0,"Gv": 20}, "mental":{"P": 0,"A": 90,"Er": 90,"Rr": 0}},
        ],
    },
}


# ── LOOKUP FUNCTIONS ───────────────────────────────────────────────────────────

def lookup_receptor(receptor_type: str, value: float) -> dict | None:
    """
    Given a receptor type and physical value, returns the matching level.
    Returns None if receptor_type unknown or no level matches.

    Example:
        lookup_receptor("temperature_skin", 33.0)
        → {"label": "elevado", "somatic":{...}, "mental":{...}, "stat": "temperature_skin", ...}
    """
    receptor = RECEPTORS.get(receptor_type)
    if not receptor:
        return None
    for level in receptor["levels"]:
        lo, hi = level["range"]
        if (lo is None or value >= lo) and (hi is None or value < hi):
            return {
                "label":   level["label"],
                "somatic": dict(level["somatic"]),
                "mental":  dict(level["mental"]),
                "stat":    receptor["stat"],
                "unit":    receptor["unit"],
                "family":  receptor["family"],
            }
    return None


def lookup_receptor_weighted(receptor_type: str, value: float, zone: str) -> dict | None:
    """
    Same as lookup_receptor but scales vectors by the homunculus density
    weight for the given body zone. Higher density = stronger CCM impact.

    Example:
        lookup_receptor_weighted("pressure", 0.5, "fingertips")  # weight 1.0
        lookup_receptor_weighted("pressure", 0.5, "thigh")       # weight 0.4
    """
    result = lookup_receptor(receptor_type, value)
    if not result:
        return None
    weight = get_zone_weight(zone, result["family"])
    result["somatic"] = {k: round(v * weight, 4) for k, v in result["somatic"].items()}
    result["mental"]  = {k: round(v * weight, 4) for k, v in result["mental"].items()}
    result["zone"]    = zone
    result["weight"]  = weight
    return result


def list_receptors() -> list[str]:
    return list(RECEPTORS.keys())
