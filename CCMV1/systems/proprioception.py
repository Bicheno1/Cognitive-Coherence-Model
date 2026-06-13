# systems/proprioception.py — CCM v4
#
# ProprioceptionSystem — reads the current physical state of the armature.
# Provides the CCM with body self-knowledge:
#   - Where is each zone (world position)
#   - What rotation is each bone at
#   - Distance between any two zones
#   - Whether a zone is near another object (proximity, not physics collision)
#
# Designed to run inside Blender (bpy available).
# All reads are non-destructive — never modifies the armature.
#
# Usage:
#   proprio = ProprioceptionSystem("Armature")
#   state   = proprio.read_all()
#   pos     = proprio.get_position("hand_r")
#   dist    = proprio.get_distance("hand_r", "head")
#   answer  = proprio.query("where is your nose")

import math

try:
    import bpy
    from mathutils import Vector
    BLENDER = True
except ImportError:
    BLENDER = False

from db.db_body import BODY_MAP, zone_from_concept


class ProprioceptionSystem:
    def __init__(self, armature_name="Armature"):
        self.armature_name = armature_name
        self._cache = {}  # last known state per zone

    # ── INTERNAL — get armature object ───────────────────────────────────────

    def _get_armature(self):
        if not BLENDER:
            return None
        obj = bpy.data.objects.get(self.armature_name)
        if obj and obj.type == "ARMATURE":
            return obj
        return None

    # ── READ — single zone ────────────────────────────────────────────────────

    def get_position(self, zone_name):
        """
        Returns world-space position of zone's bone head as (x, y, z).
        Returns None if bone not found.
        """
        zone = BODY_MAP.get(zone_name)
        if not zone:
            return None
        arm = self._get_armature()
        if not arm:
            return self._cache.get(zone_name, {}).get("position")
        bone_name = zone["bone"]
        if bone_name not in arm.pose.bones:
            return None
        pbone = arm.pose.bones[bone_name]
        world_pos = arm.matrix_world @ pbone.matrix.translation
        return (round(world_pos.x, 4),
                round(world_pos.y, 4),
                round(world_pos.z, 4))

    def get_rotation_deg(self, zone_name):
        """
        Returns current rotation of zone's bone in degrees per axis {x, y, z}.
        Uses pose bone rotation_euler (XYZ mode).
        """
        zone = BODY_MAP.get(zone_name)
        if not zone:
            return None
        arm = self._get_armature()
        if not arm:
            return self._cache.get(zone_name, {}).get("rotation_deg")
        bone_name = zone["bone"]
        if bone_name not in arm.pose.bones:
            return None
        pbone = arm.pose.bones[bone_name]
        rot = pbone.rotation_euler
        return {
            "x": round(math.degrees(rot.x), 2),
            "y": round(math.degrees(rot.y), 2),
            "z": round(math.degrees(rot.z), 2),
        }

    def get_distance(self, zone_a, zone_b):
        """
        Returns distance in Blender units between two zone bone heads.
        """
        pos_a = self.get_position(zone_a)
        pos_b = self.get_position(zone_b)
        if not pos_a or not pos_b:
            return None
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        dz = pos_b[2] - pos_a[2]
        return round(math.sqrt(dx**2 + dy**2 + dz**2), 4)

    # ── READ ALL — full body snapshot ─────────────────────────────────────────

    def read_all(self):
        """
        Returns a full snapshot of all zones: position, rotation, zone name.
        Also updates internal cache.
        """
        snapshot = {}
        for zone_name in BODY_MAP:
            pos = self.get_position(zone_name)
            rot = self.get_rotation_deg(zone_name)
            snapshot[zone_name] = {
                "bone":         BODY_MAP[zone_name]["bone"],
                "position":     pos,
                "rotation_deg": rot,
            }
            self._cache[zone_name] = snapshot[zone_name]
        return snapshot

    # ── QUERY — natural language body question ────────────────────────────────

    def query(self, text):
        """
        Answers a body location question by scanning for zone concepts in text.
        Returns a dict with zone, position, rotation, and a readable string.

        Example:
            query("where is your nose") →
            {
              "zone": "head",
              "bone": "head",
              "position": (0.0, 0.12, 1.72),
              "rotation_deg": {"x": 0.0, "y": 0.0, "z": 0.0},
              "readable": "head bone is at (0.0, 0.12, 1.72), rotation x=0.0° y=0.0° z=0.0°"
            }
        """
        words = text.lower().replace("?", "").split()
        found_zone = None

        for word in words:
            zone = zone_from_concept(word)
            if zone:
                found_zone = zone
                break

        if not found_zone:
            return {"readable": "No body zone recognized in query.", "zone": None}

        pos = self.get_position(found_zone)
        rot = self.get_rotation_deg(found_zone)
        bone = BODY_MAP[found_zone]["bone"]

        if pos:
            pos_str = f"({pos[0]}, {pos[1]}, {pos[2]})"
        else:
            pos_str = "unavailable"

        if rot:
            rot_str = f"x={rot['x']}° y={rot['y']}° z={rot['z']}°"
        else:
            rot_str = "unavailable"

        readable = f"{found_zone} [{bone}] — position {pos_str}, rotation {rot_str}"

        return {
            "zone":         found_zone,
            "bone":         bone,
            "position":     pos,
            "rotation_deg": rot,
            "readable":     readable,
        }

    # ── INPUT EVENTS — translate body events to CCM concepts ─────────────────

    def contact_event(self, zone_name, intensity=1.0, material=None):
        """
        Called when a zone makes contact with something.
        Returns a list of concept strings to feed into CCM pre_input.

        zone_name : body zone (e.g. "hand_r")
        intensity : 0.0–1.0 (how hard the contact is)
        material  : optional string ("hot", "cold", "sharp", "soft")
        """
        concepts = []
        zone = BODY_MAP.get(zone_name)
        if not zone:
            return concepts

        concepts.append("contact")
        concepts.append(zone_name)

        if intensity >= 0.7:
            concepts.append("pain")
            concepts.append("pressure")
        elif intensity >= 0.3:
            concepts.append("touch")
            concepts.append("pressure")
        else:
            concepts.append("touch")

        if material:
            concepts.append(material)

        return concepts

    def movement_event(self, zone_name, speed=1.0):
        """
        Called when a zone moves significantly.
        Returns concept strings for CCM.
        speed: 0.0–1.0 (relative movement speed)
        """
        concepts = [zone_name, "move"]
        if speed >= 0.7:
            concepts.extend(["run", "fast"])
        elif speed >= 0.3:
            concepts.extend(["walk"])
        else:
            concepts.extend(["slow"])
        return concepts
