# db/db_body.py — CCM v4
#
# Body map — 10 macro zones linking CCM concepts to armature bones.
# Each zone defines:
#   bone        : exact bone name in the Blender armature
#   concepts    : CCM concept/tag names that map to this zone
#   axes        : which rotation axes are valid for this bone (x, y, z)
#   range_deg   : (min, max) rotation in degrees per axis
#   can_move    : whether CCM output can drive this bone
#   description : human-readable zone description

BODY_MAP = {

    "head": {
        "bone":        "head",
        "concepts":    ["head", "face", "nose", "mouth", "eye", "ear", "skull"],
        "axes":        ["x", "y", "z"],
        "range_deg":   {"x": (-30, 30), "y": (-45, 45), "z": (-60, 60)},
        "can_move":    True,
        "description": "Head — full rotation, nod and turn",
    },

    "neck": {
        "bone":        "neck",
        "concepts":    ["neck", "throat", "chin"],
        "axes":        ["x", "z"],
        "range_deg":   {"x": (-20, 20), "z": (-30, 30)},
        "can_move":    True,
        "description": "Neck — tilt and turn support for head",
    },

    "spine": {
        "bone":        "spine",
        "concepts":    ["spine", "back", "torso", "chest", "stomach", "belly"],
        "axes":        ["x", "z"],
        "range_deg":   {"x": (-40, 40), "z": (-30, 30)},
        "can_move":    True,
        "description": "Spine — forward/back bend and lateral lean",
    },

    "shoulder_r": {
        "bone":        "upper_arm.R",
        "concepts":    ["shoulder", "arm", "shoulder_r", "arm_r", "right_arm"],
        "axes":        ["x", "y", "z"],
        "range_deg":   {"x": (-90, 180), "y": (-90, 90), "z": (-90, 90)},
        "can_move":    True,
        "description": "Right shoulder / upper arm",
    },

    "shoulder_l": {
        "bone":        "upper_arm.L",
        "concepts":    ["shoulder_l", "arm_l", "left_arm"],
        "axes":        ["x", "y", "z"],
        "range_deg":   {"x": (-90, 180), "y": (-90, 90), "z": (-90, 90)},
        "can_move":    True,
        "description": "Left shoulder / upper arm",
    },

    "hand_r": {
        "bone":        "hand.R",
        "concepts":    ["hand", "hand_r", "right_hand", "finger", "touch", "grab", "hold"],
        "axes":        ["x", "z"],
        "range_deg":   {"x": (-80, 80), "z": (-20, 20)},
        "can_move":    True,
        "description": "Right hand — grip and wrist rotation",
    },

    "hand_l": {
        "bone":        "hand.L",
        "concepts":    ["hand_l", "left_hand"],
        "axes":        ["x", "z"],
        "range_deg":   {"x": (-80, 80), "z": (-20, 20)},
        "can_move":    True,
        "description": "Left hand — grip and wrist rotation",
    },

    "thigh_r": {
        "bone":        "thigh.R",
        "concepts":    ["leg", "thigh", "thigh_r", "right_leg", "hip_r", "walk", "run", "kick"],
        "axes":        ["x", "z"],
        "range_deg":   {"x": (-120, 45), "z": (-45, 45)},
        "can_move":    True,
        "description": "Right thigh — walking, running, kicking",
    },

    "thigh_l": {
        "bone":        "thigh.L",
        "concepts":    ["thigh_l", "left_leg", "hip_l"],
        "axes":        ["x", "z"],
        "range_deg":   {"x": (-120, 45), "z": (-45, 45)},
        "can_move":    True,
        "description": "Left thigh — walking, running, kicking",
    },

    "foot_r": {
        "bone":        "foot.R",
        "concepts":    ["foot", "foot_r", "right_foot", "ankle_r", "step", "ground"],
        "axes":        ["x"],
        "range_deg":   {"x": (-45, 45)},
        "can_move":    True,
        "description": "Right foot — plantar/dorsiflexion",
    },

    "foot_l": {
        "bone":        "foot.L",
        "concepts":    ["foot_l", "left_foot", "ankle_l"],
        "axes":        ["x"],
        "range_deg":   {"x": (-45, 45)},
        "can_move":    True,
        "description": "Left foot — plantar/dorsiflexion",
    },
}

# Reverse lookup: concept → zone name
CONCEPT_TO_ZONE = {}
for zone_name, zone in BODY_MAP.items():
    for concept in zone["concepts"]:
        CONCEPT_TO_ZONE[concept] = zone_name


def get_zone(zone_name):
    return BODY_MAP.get(zone_name)


def zone_from_concept(concept):
    """Returns zone name for a given concept string, or None."""
    return CONCEPT_TO_ZONE.get(concept.lower())
