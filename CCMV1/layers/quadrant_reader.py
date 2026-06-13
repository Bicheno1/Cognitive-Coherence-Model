# layers/quadrant_reader.py
from core.formulas import get_rhomboid_center, get_quadrant
import math

def read_somatic_sector(state):
    keys = ["V","I","Lv","Gv"]
    cx, cy = get_rhomboid_center(state, keys)
    quad   = get_quadrant(state, keys)
    dist   = math.sqrt(cx**2 + cy**2)
    return {"quadrant": quad, "cx": round(cx,4), "cy": round(cy,4), "distance": round(dist,4)}

def read_mental_sector(state):
    keys = ["P","A","Er","Rr"]
    cx, cy = get_rhomboid_center(state, keys)
    quad   = get_quadrant(state, keys)
    dist   = math.sqrt(cx**2 + cy**2)
    return {"quadrant": quad, "cx": round(cx,4), "cy": round(cy,4), "distance": round(dist,4)}
