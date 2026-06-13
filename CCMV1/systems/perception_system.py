# systems/perception_system.py — CCM v4
#
# PerceptionSystem — camera-based environmental awareness.
# Reads visible objects in Blender scene, their custom properties,
# and translates distance to qualitative concepts for the CCM.
#
# DISTANCE CATEGORIES (in Blender metric units):
#   very_close  : < 0.5 m   — within arm's reach
#   close       : 0.5–2.0 m — nearby, social space
#   medium      : 2.0–5.0 m — same room
#   far         : 5.0–15.0m — across the space
#   very_far    : > 15.0 m  — distant
#
# OBJECT PROPERTIES (set in Blender custom properties):
#   Any key-value pair on the object is read and passed as concepts.
#   Example: object with property "temperature" = "hot" → concept "hot"
#            object with property "material" = "metal" → concept "metal"
#            object with property "edible" = True → concept "food"
#
# OUTPUT:
#   List of perception events, each with:
#     - object name
#     - distance category (qualitative)
#     - distance (metric, for internal use)
#     - concepts derived from properties
#     - raw properties dict

try:
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    BLENDER = True
except ImportError:
    BLENDER = False

# ── DISTANCE THRESHOLDS (meters) ─────────────────────────────────────────────

DISTANCE_ZONES = [
    (0.5,  "very_close"),
    (2.0,  "close"),
    (5.0,  "medium"),
    (15.0, "far"),
]
DISTANCE_FALLBACK = "very_far"

# ── PROPERTY → CONCEPT MAP ───────────────────────────────────────────────────
# Maps object property values to CCM concept strings.
# Add more as needed — these are just the common ones.

PROPERTY_CONCEPT_MAP = {
    # temperature
    "hot":         ["hot", "heat", "warm"],
    "cold":        ["cold", "cool"],
    "warm":        ["warm", "comfortable"],
    "freezing":    ["cold", "extreme_cold"],
    # material
    "metal":       ["hard", "cold", "metal"],
    "wood":        ["warm", "soft", "natural"],
    "fabric":      ["soft", "comfortable", "warm"],
    "glass":       ["hard", "fragile", "cold"],
    "water":       ["water", "wet", "cold"],
    "food":        ["food", "eat", "hunger"],
    # state
    "dangerous":   ["danger", "threat"],
    "safe":        ["safe", "security"],
    "friendly":    ["friend", "company"],
    "alive":       ["alive", "animate"],
    "edible":      ["food", "eat"],
    "drinkable":   ["water", "drink"],
    # texture/feel
    "soft":        ["soft", "comfortable"],
    "hard":        ["hard", "uncomfortable"],
    "sharp":       ["sharp", "pain", "danger"],
    "wet":         ["wet", "cold", "water"],
    "dry":         ["dry", "comfortable"],
    # smell (for future sensor expansion)
    "pleasant":    ["pleasant", "calm"],
    "unpleasant":  ["unpleasant", "discomfort"],
}

# Distance zone → concept added automatically
DISTANCE_CONCEPTS = {
    "very_close": ["very_close", "proximity", "touch"],
    "close":      ["close", "nearby"],
    "medium":     ["medium_distance", "present"],
    "far":        ["far", "distant"],
    "very_far":   ["very_far", "remote"],
}


# ── PERCEPTION SYSTEM ─────────────────────────────────────────────────────────

class PerceptionSystem:
    def __init__(self, camera_name=None, ignored_objects=None):
        """
        camera_name    : name of the camera object in the scene (None = use active)
        ignored_objects: list of object names to always skip
        """
        self.camera_name     = camera_name
        self.ignored_objects = set(ignored_objects or [])
        self._last_scan      = []

    # ── SCAN ──────────────────────────────────────────────────────────────────

    def scan(self):
        """
        Scans the current Blender scene for visible objects.
        Returns list of perception dicts.
        Each dict: {name, object_type, distance_m, distance_zone, concepts, properties}
        """
        if not BLENDER:
            return self._last_scan  # return cached in non-Blender mode

        scene  = bpy.context.scene
        camera = self._get_camera(scene)
        if not camera:
            return []

        results = []
        for obj in scene.objects:
            if obj == camera:
                continue
            if obj.name in self.ignored_objects:
                continue
            if obj.hide_viewport or obj.hide_render:
                continue

            world_pos = obj.matrix_world.translation
            co_ndc    = world_to_camera_view(scene, camera, world_pos)

            # Check if visible in camera frustum
            in_frame = (0.0 <= co_ndc.x <= 1.0 and
                        0.0 <= co_ndc.y <= 1.0 and
                        co_ndc.z > 0)
            if not in_frame:
                continue

            distance_m    = (camera.location - world_pos).length
            distance_zone = self._classify_distance(distance_m)
            properties    = self._read_properties(obj)
            concepts      = self._properties_to_concepts(properties, distance_zone)

            results.append({
                "name":          obj.name,
                "object_type":   obj.type,
                "distance_m":    round(distance_m, 3),
                "distance_zone": distance_zone,
                "concepts":      concepts,
                "properties":    properties,
            })

        self._last_scan = results
        return results

    # ── CONCEPTS FOR CCM ──────────────────────────────────────────────────────

    def get_concepts(self):
        """
        Returns flat list of all concepts from last scan.
        Ready to feed into CCM process_input.
        """
        all_concepts = []
        for item in self._last_scan:
            for c in item["concepts"]:
                if c not in all_concepts:
                    all_concepts.append(c)
        return all_concepts

    def get_closest(self):
        """Returns the closest visible object perception dict, or None."""
        if not self._last_scan:
            return None
        return min(self._last_scan, key=lambda x: x["distance_m"])

    # ── DISTANCE ──────────────────────────────────────────────────────────────

    def _classify_distance(self, meters):
        for threshold, label in DISTANCE_ZONES:
            if meters < threshold:
                return label
        return DISTANCE_FALLBACK

    # ── PROPERTIES ────────────────────────────────────────────────────────────

    def _read_properties(self, obj):
        """Reads all custom properties from object and its parent armature."""
        props = {}
        for key in obj.keys():
            if key != "_RNA_UI":
                props[key] = obj[key]
        # Also read parent armature properties
        if obj.parent and obj.parent.type == "ARMATURE":
            for key in obj.parent.keys():
                if key != "_RNA_UI" and key not in props:
                    props[key] = obj.parent[key]
        return props

    def _properties_to_concepts(self, properties, distance_zone):
        """Converts property dict + distance zone to CCM concept list."""
        concepts = []

        # Distance zone concepts
        for c in DISTANCE_CONCEPTS.get(distance_zone, []):
            if c not in concepts:
                concepts.append(c)

        # Property value concepts
        for key, val in properties.items():
            val_str = str(val).lower().strip()
            # Direct key as concept
            if val_str in ("true", "1", "yes"):
                concepts.append(key.lower())
            # Map value to concepts
            if val_str in PROPERTY_CONCEPT_MAP:
                for c in PROPERTY_CONCEPT_MAP[val_str]:
                    if c not in concepts:
                        concepts.append(c)
            # Raw string value as concept if short
            elif len(val_str) <= 20 and val_str not in ("false", "0", "no"):
                concepts.append(val_str)

        return concepts

    def _get_camera(self, scene):
        if self.camera_name:
            return bpy.data.objects.get(self.camera_name)
        return scene.camera

    # ── STATUS ────────────────────────────────────────────────────────────────

    def status(self):
        return {
            "visible_objects": len(self._last_scan),
            "objects": [
                {
                    "name":     o["name"],
                    "zone":     o["distance_zone"],
                    "distance": o["distance_m"],
                    "concepts": o["concepts"],
                }
                for o in self._last_scan
            ],
        }
