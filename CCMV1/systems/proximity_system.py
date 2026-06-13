# systems/proximity_system.py — CCM v4
#
# ProximitySystem — detects when bones from different armatures (or self)
# come within a threshold distance of each other.
#
# TOUCH THRESHOLD: 0.01 m (1 cm) — activates property reading and contact input
# PROXIMITY ZONES:
#   touch     : < 0.01 m  — direct contact, reads bone properties
#   very_close: < 0.10 m  — almost touching
#   close     : < 0.50 m  — nearby influence (warmth, etc.)
#   near      : < 1.00 m  — awareness zone
#
# BONE PROPERTIES (set as custom properties on bones in Blender):
#   temperature: "hot" | "cold" | "warm"
#   material:    "fabric" | "metal" | "wood" | "skin" | "ice" | ...
#   texture:     "soft" | "hard" | "sharp" | "smooth" | ...
#   edible:      True/False
#   drinkable:   True/False
#   any custom:  passed through as concept
#
# COMMODITY EFFECT:
#   touch of soft/warm → commodity +
#   touch of sharp/cold → commodity -
#   prolonged bad posture (bone near joint limit) → commodity -
#
# OUTPUT per contact event:
#   {zone_a, bone_a, zone_b, bone_b, distance_m, proximity_zone, concepts, commodity_delta}

import math

try:
    import bpy
    BLENDER = True
except ImportError:
    BLENDER = False

from db.db_body import BODY_MAP

# ── THRESHOLDS (meters) ───────────────────────────────────────────────────────

TOUCH_THRESHOLD      = 0.01   # direct contact — reads properties
VERY_CLOSE_THRESHOLD = 0.10
CLOSE_THRESHOLD      = 0.50
NEAR_THRESHOLD       = 1.00

PROXIMITY_ZONES = [
    (TOUCH_THRESHOLD,      "touch"),
    (VERY_CLOSE_THRESHOLD, "very_close"),
    (CLOSE_THRESHOLD,      "close"),
    (NEAR_THRESHOLD,       "near"),
]

# ── BONE PROPERTY → CONCEPT + COMMODITY MAP ──────────────────────────────────

BONE_PROP_MAP = {
    # temperature
    "hot":      {"concepts": ["hot", "heat", "warm"],            "commodity": -1.0},
    "cold":     {"concepts": ["cold", "temperature"],            "commodity": -1.5},
    "warm":     {"concepts": ["warm", "comfortable"],            "commodity": +1.0},
    "freezing": {"concepts": ["cold", "pain", "temperature"],    "commodity": -2.0},
    # material / texture
    "skin":     {"concepts": ["touch", "contact", "company"],    "commodity": +0.5},
    "fabric":   {"concepts": ["soft", "comfortable", "warm"],    "commodity": +1.0},
    "metal":    {"concepts": ["hard", "cold", "metal"],          "commodity": -0.5},
    "wood":     {"concepts": ["natural", "solid"],               "commodity":  0.0},
    "ice":      {"concepts": ["cold", "pain", "temperature"],    "commodity": -2.0},
    "fur":      {"concepts": ["soft", "warm", "comfortable"],    "commodity": +1.5},
    "sharp":    {"concepts": ["sharp", "pain", "danger"],        "commodity": -3.0},
    "soft":     {"concepts": ["soft", "comfortable"],            "commodity": +1.0},
    "hard":     {"concepts": ["hard", "uncomfortable"],          "commodity": -0.5},
    "rough":    {"concepts": ["rough", "uncomfortable"],         "commodity": -0.5},
    "smooth":   {"concepts": ["smooth", "comfortable"],          "commodity": +0.5},
    "wet":      {"concepts": ["wet", "water", "cold"],           "commodity": -0.5},
    "dry":      {"concepts": ["dry", "comfortable"],             "commodity": +0.2},
    # food/taste — tongue bone interactions
    "sweet":    {"concepts": ["sweet", "food", "eat"],           "commodity": +1.0},
    "cold_food":{"concepts": ["cold", "food", "eat"],            "commodity":  0.0},
    "moist":    {"concepts": ["wet", "food"],                    "commodity":  0.0},
    "bitter":   {"concepts": ["bitter", "unpleasant"],           "commodity": -0.5},
    # clothing properties
    "tight":    {"concepts": ["tight", "uncomfortable"],         "commodity": -1.0},
    "loose":    {"concepts": ["loose", "comfortable"],           "commodity": +0.5},
    "heavy":    {"concepts": ["heavy", "tired"],                 "commodity": -0.5},
    # social
    "friendly": {"concepts": ["friend", "company", "safe"],      "commodity": +1.5},
    "hostile":  {"concepts": ["danger", "threat", "unsafe"],     "commodity": -2.0},
}

# ── POSTURE COMFORT — commodity from bone range usage ────────────────────────
# If a bone is using more than POSTURE_DISCOMFORT_THRESHOLD of its range
# on any axis, commodity starts dropping.

POSTURE_DISCOMFORT_THRESHOLD = 0.75  # 75% of range = starts being uncomfortable
POSTURE_DISCOMFORT_RATE      = -0.05  # commodity delta per tick per uncomfortable bone


# ── PROXIMITY SYSTEM ──────────────────────────────────────────────────────────

class ProximitySystem:
    def __init__(self, self_armature_name="Armature"):
        self.self_armature_name = self_armature_name
        self._contacts          = []  # last frame contacts

    # ── SCAN — check all bone pairs between armatures ─────────────────────────

    def scan(self, other_armature_names=None):
        """
        Scans for bone proximity between self armature and others.
        Also scans self-armature bones against each other (self-contact).

        other_armature_names: list of other armature object names to check.
                              If None, scans all armatures in scene.
        Returns list of contact event dicts.
        """
        if not BLENDER:
            return self._contacts

        self_arm = bpy.data.objects.get(self.self_armature_name)
        if not self_arm or self_arm.type != "ARMATURE":
            return []

        # Collect other armatures
        if other_armature_names is None:
            others = [obj for obj in bpy.data.objects
                      if obj.type == "ARMATURE" and obj.name != self.self_armature_name]
        else:
            others = [bpy.data.objects.get(n) for n in other_armature_names
                      if bpy.data.objects.get(n)]

        contacts = []

        # Check self bones vs other armature bones
        for other_arm in others:
            events = self._check_armature_pair(self_arm, other_arm)
            contacts.extend(events)

        self._contacts = contacts
        return contacts

    def _check_armature_pair(self, arm_a, arm_b):
        """Checks all bone combinations between two armatures."""
        events = []
        world_a = arm_a.matrix_world
        world_b = arm_b.matrix_world

        for bone_name_a, zone_a in BODY_MAP.items():
            bname_a = zone_a["bone"]
            if bname_a not in arm_a.pose.bones:
                continue
            pbone_a  = arm_a.pose.bones[bname_a]
            pos_a    = world_a @ pbone_a.matrix.translation

            for bone_name_b in arm_b.pose.bones.keys():
                pbone_b = arm_b.pose.bones[bone_name_b]
                pos_b   = world_b @ pbone_b.matrix.translation

                dist = (pos_b - pos_a).length
                prox_zone = self._classify_proximity(dist)
                if prox_zone is None:
                    continue

                # Read bone properties from other armature
                bone_props = self._read_bone_properties(arm_b, bone_name_b)
                concepts, commodity_delta = self._props_to_concepts(
                    bone_props, prox_zone, dist
                )

                events.append({
                    "zone_a":        bone_name_a,
                    "bone_a":        bname_a,
                    "armature_b":    arm_b.name,
                    "bone_b":        bone_name_b,
                    "distance_m":    round(dist, 4),
                    "proximity_zone": prox_zone,
                    "concepts":      concepts,
                    "commodity_delta": commodity_delta,
                    "properties":    bone_props,
                })

        return events

    # ── POSTURE COMFORT ───────────────────────────────────────────────────────

    def compute_posture_commodity(self, proprioception=None):
        """
        Checks how much of each bone's range is being used.
        Returns commodity delta for this tick (negative = uncomfortable posture).
        Also returns list of uncomfortable bones.
        """
        if not BLENDER or proprioception is None:
            return 0.0, []

        arm = bpy.data.objects.get(self.self_armature_name)
        if not arm:
            return 0.0, []

        total_delta    = 0.0
        uncomfortable  = []

        for zone_name, zone in BODY_MAP.items():
            bone_name = zone["bone"]
            if bone_name not in arm.pose.bones:
                continue

            import math as _math
            pbone = arm.pose.bones[bone_name]
            ranges = zone.get("range_deg", {})

            for axis, (lo, hi) in ranges.items():
                current_deg = _math.degrees(getattr(pbone.rotation_euler, axis))
                range_span  = hi - lo
                if range_span <= 0:
                    continue
                # How far from center of range (0 = center, 1 = at limit)
                center   = (hi + lo) / 2.0
                usage    = abs(current_deg - center) / (range_span / 2.0)

                if usage > POSTURE_DISCOMFORT_THRESHOLD:
                    overshoot = usage - POSTURE_DISCOMFORT_THRESHOLD
                    delta = POSTURE_DISCOMFORT_RATE * overshoot
                    total_delta += delta
                    uncomfortable.append(f"{zone_name}.{axis} ({current_deg:.1f}°)")

        return total_delta, uncomfortable

    # ── CONCEPTS FOR CCM ──────────────────────────────────────────────────────

    def get_concepts(self):
        """Flat list of all concepts from last scan."""
        all_concepts = []
        for contact in self._contacts:
            for c in contact["concepts"]:
                if c not in all_concepts:
                    all_concepts.append(c)
        return all_concepts

    def get_total_commodity_delta(self):
        """Sum of all commodity deltas from contacts this scan."""
        return sum(c["commodity_delta"] for c in self._contacts)

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _classify_proximity(self, dist):
        for threshold, label in PROXIMITY_ZONES:
            if dist <= threshold:
                return label
        return None  # out of range — ignore

    def _read_bone_properties(self, armature_obj, bone_name):
        """Reads custom properties from a pose bone."""
        props = {}
        if bone_name in armature_obj.pose.bones:
            pbone = armature_obj.pose.bones[bone_name]
            for key in pbone.keys():
                if key != "_RNA_UI":
                    props[key] = pbone[key]
        return props

    def _props_to_concepts(self, properties, prox_zone, distance):
        """Converts bone properties + proximity zone to concepts and commodity delta."""
        concepts = [prox_zone]  # proximity zone itself as concept
        commodity_delta = 0.0

        # Scale effect by distance — closer = stronger
        if prox_zone == "touch":
            scale = 1.0
        elif prox_zone == "very_close":
            scale = 0.6
        elif prox_zone == "close":
            scale = 0.3
        else:
            scale = 0.1

        for key, val in properties.items():
            val_str = str(val).lower().strip()
            if val_str in BONE_PROP_MAP:
                entry = BONE_PROP_MAP[val_str]
                for c in entry["concepts"]:
                    if c not in concepts:
                        concepts.append(c)
                commodity_delta += entry["commodity"] * scale
            else:
                # Pass through as raw concept
                if val_str not in ("true", "false", "0", "1") and len(val_str) <= 20:
                    concepts.append(val_str)

        return concepts, round(commodity_delta, 3)

    # ── STATUS ────────────────────────────────────────────────────────────────

    def status(self):
        return {
            "contacts":        len(self._contacts),
            "commodity_delta": self.get_total_commodity_delta(),
            "events": [
                {
                    "zone_a":   c["zone_a"],
                    "bone_b":   c["bone_b"],
                    "zone":     c["proximity_zone"],
                    "dist":     c["distance_m"],
                    "concepts": c["concepts"],
                }
                for c in self._contacts
            ],
        }
