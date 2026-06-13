# layers/tag_scaler.py
# Modifies a tag's impact based on how close the current state is to the center
#
# Near center → tag impacts with reduced values (system abierto, baja reactividad)
# Far from center → tag impacts with full or amplified value (system tenso)
#
# Separate thresholds per engine:
#   mental  (0-200): low<20  normal<50  active<90  saturated<170  collapse+
#   Somatic (0-400): low<40  normal<100 active<180 saturated<340  collapse+

CENTER_SCALE  = 0.4    # reduction near center
TENSION_SCALE = 1.2    # amplification when already tense


def _thresholds(keys):
    """Returns (low_threshold, tension_threshold) depending on somatic or mental."""
    if any(k in keys for k in ("V", "I", "Lv", "Gv")):
        return 40, 180   # somatic: low=40, active=180
    return 20, 90        # mental:  low=20, active=90


def scale_tag(tag_values, distance, keys):
    """
    Scales a tag's values based on the current state's distance to center.

    Args:
        tag_values: dict with tag values (V, I, Lv, Gv) or (P, A, Er, Rr)
        distance:   current distance from point to center (0.0 = center)
        keys:       list of keys to scale

    Returns:
        dict with scaled values
    """
    low_thresh, tension_thresh = _thresholds(keys)

    if distance < low_thresh:
        factor = CENTER_SCALE + (distance / low_thresh) * (1.0 - CENTER_SCALE)
    elif distance > tension_thresh:
        factor = TENSION_SCALE
    else:
        factor = 1.0

    scaled = {}
    for k in keys:
        if k in tag_values and isinstance(tag_values[k], (int, float)):
            scaled[k] = tag_values[k] * factor
        elif k in tag_values:
            scaled[k] = tag_values[k]
    return scaled
