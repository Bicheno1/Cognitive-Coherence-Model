# systems/body_output.py — CCM v4
#
# BodyOutput — translates CCM sector/state into armature bone movements.
# Reads the CCM final_state and drives the armature accordingly.
#
# MOVEMENT MODEL:
#   CCM output sector (e.g. "inviable-localized", "viable-global") maps
#   to a body posture pattern — a set of bone rotations.
#   These are additive deltas, not absolute poses, so they blend naturally.
#
# FORMAT:
#   Each move is:  (zone_name, axis, degrees)
#   Executed as:   bone.rotation_euler.{axis} += radians(degrees)
#   Clamped to the zone's defined range_deg.
#
# POSTURE PATTERNS:
#   Mapped from somatic sector × mental sector intersection.
#   You can add more patterns — just follow the same structure.

import math

try:
    import bpy
    BLENDER = True
except ImportError:
    BLENDER = False

from db.db_body import BODY_MAP

# ── POSTURE PATTERNS ──────────────────────────────────────────────────────────
# Key: (somatic_quadrant, mental_quadrant)
# Value: list of (zone_name, axis, delta_degrees)
# Use small deltas — these are applied per cycle, they accumulate naturally.

POSTURE_PATTERNS = {

    # THREAT / FEAR — curled inward, head down, arms up defensively
    ("inviable-localized", "absent-emotional"): [
        ("head",       "x", -15.0),   # head down
        ("spine",      "x", -10.0),   # hunch forward
        ("shoulder_r", "z",  20.0),   # arms slightly raised
        ("shoulder_l", "z", -20.0),
    ],

    # PAIN / OVERWHELM — collapse, contraction
    ("inviable-localized", "absent-rational"): [
        ("head",       "x", -20.0),
        ("spine",      "x", -15.0),
        ("shoulder_r", "x", -15.0),
        ("shoulder_l", "x", -15.0),
    ],

    # ALERT / VIGILANT — upright, head scanning
    ("inviable-global", "absent-emotional"): [
        ("head",       "z",  10.0),   # slight head turn
        ("spine",      "x",   5.0),   # slight lean forward
        ("shoulder_r", "x",  10.0),
        ("shoulder_l", "x",  10.0),
    ],

    # CALM / PRESENT — neutral upright posture
    ("viable-global", "present-rational"): [
        ("head",       "x",   0.0),
        ("spine",      "x",   0.0),
        ("shoulder_r", "x",   0.0),
        ("shoulder_l", "x",   0.0),
    ],

    # RELAXED / CONTENT — slight slump, open posture
    ("viable-global", "present-emotional"): [
        ("spine",      "x",  -5.0),   # gentle backward lean
        ("shoulder_r", "z", -10.0),   # arms relaxed down
        ("shoulder_l", "z",  10.0),
        ("head",       "x",   5.0),   # head slightly up
    ],

    # ENGAGED / CURIOUS — forward lean, head up
    ("viable-localized", "present-rational"): [
        ("head",       "x",  10.0),   # head up attentive
        ("spine",      "x",   8.0),   # lean forward
        ("shoulder_r", "x",  15.0),
        ("shoulder_l", "x",  15.0),
    ],

    # DISTRESSED / WITHDRAWN — curled, head down
    ("inviable-global", "absent-rational"): [
        ("head",       "x", -25.0),
        ("spine",      "x", -20.0),
        ("shoulder_r", "z",  15.0),
        ("shoulder_l", "z", -15.0),
        ("thigh_r",    "x",  10.0),
        ("thigh_l",    "x",  10.0),
    ],
}

# Fallback pattern — neutral reset
NEUTRAL_PATTERN = [
    ("head",       "x",  0.0),
    ("spine",      "x",  0.0),
    ("shoulder_r", "x",  0.0),
    ("shoulder_l", "x",  0.0),
]


# ── BODY OUTPUT ───────────────────────────────────────────────────────────────

class BodyOutput:
    def __init__(self, armature_name="Armature"):
        self.armature_name = armature_name

    def _get_armature(self):
        if not BLENDER:
            return None
        obj = bpy.data.objects.get(self.armature_name)
        if obj and obj.type == "ARMATURE":
            return obj
        return None

    def _clamp_rotation(self, zone_name, axis, degrees):
        """Clamps degrees to the zone's defined range."""
        zone = BODY_MAP.get(zone_name)
        if not zone:
            return degrees
        ranges = zone.get("range_deg", {})
        if axis in ranges:
            lo, hi = ranges[axis]
            return max(lo, min(hi, degrees))
        return degrees

    def _apply_move(self, arm, zone_name, axis, delta_degrees):
        """
        Applies a delta rotation to a bone, clamped to its range.
        Returns a readable string describing what was done.
        """
        zone = BODY_MAP.get(zone_name)
        if not zone or not zone.get("can_move"):
            return None
        if axis not in zone.get("axes", []):
            return None

        bone_name = zone["bone"]
        if arm and bone_name in arm.pose.bones:
            pbone = arm.pose.bones[bone_name]
            current_deg = math.degrees(getattr(pbone.rotation_euler, axis))
            target_deg  = self._clamp_rotation(zone_name, axis, current_deg + delta_degrees)
            setattr(pbone.rotation_euler, axis, math.radians(target_deg))
            return f"move {bone_name} {target_deg:+.1f}° {axis.upper()}"
        else:
            # No armature available — return the command string only
            target_deg = self._clamp_rotation(zone_name, axis, delta_degrees)
            return f"move {zone['bone']} {target_deg:+.1f}° {axis.upper()}"

    # ── MAIN ENTRY — from CCM final_state ────────────────────────────────────

    def apply_state(self, final_state):
        """
        Reads CCM final_state, selects a posture pattern, applies it.
        Returns list of executed move strings.
        """
        somatic_q = final_state.get("somatic", {}).get("sector", {}).get("quadrant", "")
        mental_q  = final_state.get("mental",  {}).get("sector", {}).get("quadrant", "")

        pattern = POSTURE_PATTERNS.get((somatic_q, mental_q), NEUTRAL_PATTERN)

        arm      = self._get_armature()
        executed = []

        for zone_name, axis, delta_deg in pattern:
            result = self._apply_move(arm, zone_name, axis, delta_deg)
            if result:
                executed.append(result)

        return executed

    # ── DIRECT MOVE — explicit command ────────────────────────────────────────

    def move(self, zone_name, axis, delta_degrees):
        """
        Direct move command. Use for proprioception-driven responses.
        Example: body_out.move("head", "z", 30.0)
        Returns readable string.
        """
        arm = self._get_armature()
        return self._apply_move(arm, zone_name, axis, delta_degrees)

    def reset_zone(self, zone_name):
        """Resets all axes of a zone to 0."""
        zone = BODY_MAP.get(zone_name)
        if not zone:
            return
        arm = self._get_armature()
        if arm and zone["bone"] in arm.pose.bones:
            pbone = arm.pose.bones[zone["bone"]]
            pbone.rotation_euler.x = 0.0
            pbone.rotation_euler.y = 0.0
            pbone.rotation_euler.z = 0.0

    def reset_all(self):
        """Resets all zones to neutral."""
        for zone_name in BODY_MAP:
            self.reset_zone(zone_name)

    # ── READABLE SUMMARY ──────────────────────────────────────────────────────

    def describe_move(self, zone_name, axis, delta_degrees):
        """Returns the move string without executing it."""
        zone = BODY_MAP.get(zone_name)
        if not zone:
            return f"unknown zone: {zone_name}"
        target = self._clamp_rotation(zone_name, axis, delta_degrees)
        return f"move {zone['bone']} {target:+.1f}° {axis.upper()}"
