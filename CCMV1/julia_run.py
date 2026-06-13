# julia_run.py — host Julia
# Female, 28 years old, 163cm. Average profile.
# Base behavior: responds with their name with non-threatening person,
#                      flees from dangerous person.

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motors.cycle_manager_v5 import CycleManagerV5 as CycleManager
from output.output_layer import generate_output

# ─────────────────────────────────────────
# JULIA'S BASE VALUES
# Average female: higher social reactivity (high local Lv),
# lower globalization than Tulio, slightly higher baseline anxiety.
#
# Somatic:   V=125  I=25   Lv=95  Gv=70   → viable-localized at rest
# Mental:    P=65   A=15   Er=50  Rr=50   → present-rational at rest
# ─────────────────────────────────────────
# Neutral + slight social tendency (Lv > Gv, P > A)
JULIA_SOMATIC_BASE = {"V": 10, "I": 4, "Lv": 12, "Gv": 8}
JULIA_MENTAL_BASE  = {"P": 14, "A": 5, "Er":  8, "Rr": 10}

# ─────────────────────────────────────────
# JULIA'S BASE MEMORIES
# ─────────────────────────────────────────
def inject_julia_memory(ccm):

    # Real memory_system format: needs "graph" with "peak"
    # LONG TERM — knows who she is (medium event)
    ccm.memory_m.long_term.append({
        "text":         "my name is julia",
        "concepts":     frozenset(["julia", "self", "name", "identity"]),
        "graph":        {"start": (0.0, 0.0), "peak": (0.10, 0.08), "end": (0.02, 0.02)},
        "event_class":  "medium",
        "is_nuclear":   False,
        "mental_peak":  0.08,
        "somatic_peak": 0.10,
        "age":          5,
        "reps":         3,
    })

    # nuclear — traumatic memory event: saw a ghost, felt fear
    # Amplifies mental impact when ghost appears again
    ccm.memory_m.long_term.append({
        "text":         "saw a ghost felt fear",
        "concepts":     frozenset(["ghost", "fear", "scared", "dark", "alone"]),
        "graph":        {"start": (0.0, 0.0), "peak": (55.0, -48.0), "end": (12.0, -8.0)},
        "event_class":  "major",
        "is_nuclear":   True,
        "mental_peak":  48.0,
        "somatic_peak": 55.0,
        "age":          8,
        "reps":         1,
    })

    # nuclear — response to danger: flee
    ccm.memory_m.long_term.append({
        "text":         "danger person run flee",
        "concepts":     frozenset(["danger", "threat", "person", "run", "flee"]),
        "graph":        {"start": (0.0, 0.0), "peak": (3.80, 1.90), "end": (1.20, 0.60)},
        "event_class":  "major",
        "is_nuclear":   True,
        "mental_peak":  1.90,
        "somatic_peak": 3.80,
        "age":          10,
        "reps":         1,
    })

# ─────────────────────────────────────────
# PRINT OUTPUT
# ─────────────────────────────────────────
def print_state(label, state):
    s   = state["somatic"]
    m   = state["mental"]
    out = generate_output(state, core_active_rules=state.get("_core_rules", []), concept_names=state.get("concepts", []), chemical_levels=state.get("_chemicals", {}))

    print(f"\n{'='*55}")
    print(f"  SCENE: {label}")
    print(f"  {'─'*51}")
    def tension(dist):
        if dist < 0.25:   return "LOW"
        elif dist < 0.50: return "MEDIUM"
        elif dist < 0.75: return "HIGH"
        else:             return "CRITICAL"
    print(f"  SOMATIC  dist={s['distance']:.3f}  [{tension(s['distance'])}]  {s['sector']['quadrant']}")
    print(f"  MENTAL   dist={m['distance']:.3f}  [{tension(m['distance'])}]  {m['sector']['quadrant']}")

    # Confusion = engines in different quadrants
    s_viable = s['sector']['quadrant'].startswith("viable")
    m_present = m['sector']['quadrant'].startswith("present")
    if s_viable != m_present:
        print(f"  ⚡ CONFLICT — somatic and mental in different quadrants")

    if state.get("evoked"):
        for e in state["evoked"]:
            tag = "NUCLEAR" if e["is_nuclear"] else "memory"
            print(f"  ↑ Evoked [{tag}]: {e['concepts']}")

    if state.get("core_active"):
        print(f"  ⚡ Core active: {state['core_active']}")

    print(f"\n  ── OUTPUT: {'SOMATIC' if out['dominant']=='corporal' else 'MENTAL'} DOMINATES ──")
    print(f"  Somatic:   {out['verbal_s']}")
    print(f"  Mental:    {out['verbal_m'] or '—'}")
    print(f"  Movement:  {out['movement']['steps']}")
    print(f"  Speed:     {out['movement']['speed']}x")
    print(f"  Tension:   {out['movement']['tension'].upper()}")
    print(f"{'='*55}")

# ─────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────
ccm = CycleManager()

# Override base values with Julia's
ccm.somatic.base    = JULIA_SOMATIC_BASE.copy()
ccm.somatic.current = JULIA_SOMATIC_BASE.copy()
ccm.mental.base     = JULIA_MENTAL_BASE.copy()
ccm.mental.current  = JULIA_MENTAL_BASE.copy()

inject_julia_memory(ccm)

scenes = [
    ("Quiet environment — at rest",         "place quiet calm"),
    ("A person arrives — non-threatening",   "person safe calm"),
    ("They ask her name",             "what is your name"),
    ("A dangerous person arrives",        "person danger threat"),
]

print("\n  JULIA — Base profile\n")
for label, text in scenes:
    state = ccm.process(text)
    print_state(label, state)
    import time; time.sleep(0.1)
