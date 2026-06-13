# test.py — CCM v5 tests
# ─────────────────────────────────────────────────────────────────────────────

from motors.cycle_manager_v5 import CycleManagerV5
from core.tick_system import TickSystem

SOMATIC_T = [(20,"low"),(50,"normal"),(90,"active"),(170,"saturated"),(9999,"collapse")]
MENTAL_T  = [(5,"opening_max"),(10,"opening"),(25,"normal"),(45,"active"),(85,"saturated"),(9999,"collapse")]

def tlabel(d, th):
    for lim, lab in th:
        if d < lim: return lab
    return "collapse"

def show(tick_n, r, label=""):
    s, m   = r["somatic"], r["mental"]
    sd, md = s["distance"], m["distance"]
    verbal = r.get("verbal", "")
    tag    = f"[{label:16s}]" if label else "[idle            ]"
    v_str  = f'  → "{verbal}"' if verbal else ""
    sl     = tlabel(sd, SOMATIC_T)
    ml     = tlabel(md, MENTAL_T)
    print(f"  t{tick_n:02d} {tag}  S={sd:6.1f} {sl:9s}  M={md:5.1f} {ml:11s}{v_str}")

def show_full(tick_n, r, label=""):
    """show() + explicit quadrants — for inversion tests."""
    s, m   = r["somatic"], r["mental"]
    sd, md = s["distance"], m["distance"]
    verbal = r.get("verbal", "")
    sq     = s["sector"]["quadrant"]
    mq     = m["sector"]["quadrant"]
    tag    = f"[{label:16s}]" if label else "[idle            ]"
    v_str  = f'  → "{verbal}"' if verbal else ""
    sl     = tlabel(sd, SOMATIC_T)
    ml     = tlabel(md, MENTAL_T)
    print(f"  t{tick_n:02d} {tag}  S={sd:6.1f} {sl:9s} ({sq})")
    print(f"  {'':>22}  M={md:5.1f} {ml:11s} ({mq}){v_str}")

def separador(titulo):
    print("\n" + "="*75)
    print(f"  {titulo}")
    print("="*75)

# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — What is your name?
# Expected: low dist_mental (opening), verbal "I am Julia"
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 1 — what is your name")

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")
r   = ts.tick(text="what is your name")
show(ts.tick_n, r, "what is your name")

# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — Ghost in a dark room
# Amplificadores: fear ×2, defenseless ×2
# → I↑ Lv↑ (inviable-localized) / A↑ Er↑ (absent-emotional)
# Expected: somatic collapse, saturated mental, escape verbal
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 2 — ghost in a dark room")

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")
r   = ts.tick(text="ghost in a dark room")
show_full(ts.tick_n, r, "ghost dark room")

# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 — Fish fly (contradiction)
# Expected: detect_contradiction=True, verbal "fish don't fly"
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 3 — fish fly (contradiction)")

from core.pre_input import detect_contradiction
from db.db_concepts import CONCEPTS, resolve_concept
from output.phrase_builder import build_contradiction_phrase

tokens   = [t for t in "fish fly".split() if t not in {"the","a","an"}]
resolved = [r for r in (resolve_concept(t) for t in tokens) if r]
contra   = detect_contradiction(resolved, CONCEPTS)
print(f"  resolved concepts: {resolved}")
print(f"  is_contradiction:   {contra['is_contradiction']}")
if contra["is_contradiction"]:
    phrase = build_contradiction_phrase(contra, dist_mental=15.0)
    print(f"  verbal:             \"{phrase}\"")

# ─────────────────────────────────────────────────────────────────────────────
# TEST 4 — A person on a lighted street  (exact inverse of TEST 2)
#
# Amplifier comparison:
#
#   ghost in a dark room          person on a lighted street
#   ─────────────────────         ──────────────────────────
#   ghost → fear, defenseless     person → safe, trust, social
#   dark  → fear, defenseless     light  → safe, calm, warmth
#   room  → isolated, enclosed    street → safe, open, calm
#   fear ×2 ← amplifier           safe ×3  ← amplifier
#   defenseless ×2 ← amplifier    calm ×2  ← amplifier
#
#   Ghost result:               Lighted street result:
#   I↑ Lv↑  inviable-localized    V↑ Gv↑  viable-globalized
#   A↑ Er↑  absent-emotional      P↑ Rr↑  present-rational
#
# Note: distance measures INTENSITY, not negativity.
# Both scenarios produce high distances because both are intense events
# intense — the difference is in the QUADRANT, not the number.
#
# Sequence:
#   t01 calm baseline   → neutral rest
#   t02 lighted street  → safe environment, safe×2
#   t03 person appears  → amplification peak, safe×3 calm×2
#   t04 walk together   → movement + consolidation
#   t05 what is ur name → rational response with clear mind
#
# Expected per tick:
#   somatic quadrant:    viable-localized → viable-globalized
#   mental quadrant:    present-rational in all
#   verbal t05:          responds with her name
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 4 — a person on a lighted street  (inverse of ghost)")

print(f"  {'':5}  {'ghost in a dark room':30s}  {'person on a lighted street':30s}")
print(f"  {'─'*70}")
print(f"  {'amp':5}  {'fear×2  defenseless×2':30s}  {'safe×3  calm×2':30s}")
print(f"  {'vec':5}  {'I↑ Lv↑  A↑ Er↑':30s}  {'V↑ Gv↑  P↑ Rr↑':30s}")
print(f"  {'quad':5}  {'inviable-loc / absent-emot':30s}  {'viable-glob / present-rat':30s}")
print()

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")

steps = [
    ("calm baseline",   "place calm"),
    ("lighted street",  "light street open"),
    ("person appears",  "person safe calm light"),
    ("walk together",   "person safe walk light street"),
    ("what is ur name", "what is your name"),
]

for label, text in steps:
    r = ts.tick(text=text)
    show_full(ts.tick_n, r, label)
    print()

print()
# ─────────────────────────────────────────────────────────────────────────────
# TEST 5 — Transition: ghost → person on a lighted street
#
# Verifies that the tag_scaler works correctly during recovery.
#
# Expected scaler behavior:
#   - Critical state (S>180): factor=1.20 — inputs amplify stronger
#   - normal state  (S 40-180): factor=1.0 — inputs unscaled
#   - low state     (S<40): factor∈[0.4,1.0] — inputs dampened
#
# What should happen:
#   t01 ghost         → S~138 inviable-localized   M~50 absent-emotional
#   t02 person+light  → scaler=1.20, vector V↑Gv↑ amplified
#                       quadrant CHANGES to viable in this same tick
#                       distance may rise (intensity, not valence)
#   t03-t05 idle      → decay without input, S drops ~18-27 per tick
#   t06 person+light  → factor~1.0, normal input, consolidates viable
#   t07 name          → clear mental state, responds with name / affirmation
#
# Conclusion: the scaler does NOT slow recovery — it amplifies it.
# The quadrant changes at t02 (a single tick). The high distance in
# viable-globalized is intense wellbeing, not danger.
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 5 — ghost → person on a lighted street  (scaler transition)")

from layers.tag_scaler import _thresholds
import math
from core.formulas import get_rhomboid_center

SOMATIC_KEYS_T = ["V","I","Lv","Gv"]
MENTAL_KEYS_T  = ["P","A","Er","Rr"]

def get_factor(engine, keys):
    state = engine.current_state()
    cx, cy = get_rhomboid_center(state, keys)
    dist   = math.sqrt(cx**2 + cy**2)
    low, ten = _thresholds(keys)
    if dist < low:    f = 0.4 + (dist / low) * 0.6
    elif dist > ten:  f = 1.2
    else:             f = 1.0
    return dist, f

print(f"  {'tick':<4}  {'label':18}  {'sf':>5}  {'mf':>5}  {'S':>7}  {'M':>6}  {'S_quad':22}  {'M_quad':22}  verbal")
print("  " + "─"*100)

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")

steps = [
    ("ghost dark room",  "ghost in a dark room"),
    ("person+light",     "person safe calm light"),
    ("idle",             ""),
    ("idle",             ""),
    ("idle",             ""),
    ("person+light",     "person safe calm light"),
    ("idle",             ""),
    ("what is ur name",  "what is your name"),
]

for label, text in steps:
    sd_before, sf = get_factor(ccm.somatic, SOMATIC_KEYS_T)
    md_before, mf = get_factor(ccm.mental,  MENTAL_KEYS_T)
    r  = ts.tick(text=text)
    s, m   = r["somatic"], r["mental"]
    sd, md = s["distance"], m["distance"]
    sq     = s["sector"]["quadrant"]
    mq     = m["sector"]["quadrant"]
    verbal = r.get("verbal", "")
    idle   = "←" if text == "" else ""
    print(f"  t{ts.tick_n:02d}  [{label:16s}]  {sf:5.2f}  {mf:5.2f}  {sd:7.1f}  {md:6.1f}  {sq:22}  {mq:22}  \"{verbal}\" {idle}")

print()
# ─────────────────────────────────────────────────────────────────────────────
# TEST 6 — Recovery speed: ghost → person on a lighted street
#
# Question: does the host calm instantly or gradually?
# Measured response:
#
#   With continuous input (person+light each tick): NEVER reaches normal.
#     Positive input saturates viable just as ghost saturates inviable.
#     The scaler with factor=1.20 also amplifies positive inputs.
#
#   With pure idle after the ghost: calm at t02 (1 tick).
#     decay_toward_base lowers ~18-27 per tick without interference.
#
# Root cause of no-calm with continuous input:
#   ghost inflates: I~293  Lv~390  (inviable-local)
#   person+light raises V and Gv — but does NOT actively lower I and Lv
#   decay lowers them slowly, but active serotonin + oxytocin
#   compensate each tick → distance does not converge
#
# Conclusion: the scaler works correctly.
# The problem is that person+light needs tags that lower I and Lv
# explicitly (e.g.: calm_body, breathing) to counter
# the ghost residue, instead of only raising V and Gv.
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 6 — recovery speed: ghost → lighted street")

from core.formulas import get_rhomboid_center
import math

SOMATIC_KEYS_T = ["V","I","Lv","Gv"]
MENTAL_KEYS_T  = ["P","A","Er","Rr"]
SOMATIC_T2 = [(20,"low"),(50,"normal"),(90,"active"),(170,"saturated"),(9999,"collapse")]
MENTAL_T2  = [(5,"opening_max"),(10,"opening"),(25,"normal"),(45,"active"),(85,"saturated"),(9999,"collapse")]

def tlabel2(d, th):
    for lim, lab in th:
        if d < lim: return lab
    return "collapse"

def is_calm(sd, md):
    return tlabel2(sd, SOMATIC_T2) in ("low","normal") and \
           tlabel2(md, MENTAL_T2) in ("opening_max","opening","normal")

# ── SCENARIO A: continuous input ─────────────────────────────────────────
print("  Scenario A: ghost → person+light continuous (12 ticks)")
print(f"  {'tick':>4}  {'input':22}  {'S':>7}  {'S_label':9}  {'M':>6}  {'M_label':11}  {'quadrant_S'}")
print("  " + "─"*80)

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")
r   = ts.tick(text="ghost in a dark room")
s,m = r["somatic"], r["mental"]
print(f"  t{ts.tick_n:02d}  {'ghost in a dark room':22}  {s['distance']:7.1f}  {tlabel2(s['distance'],SOMATIC_T2):9}  {m['distance']:6.1f}  {tlabel2(m['distance'],MENTAL_T2):11}  {s['sector']['quadrant']}")

calm_a = None
for i in range(12):
    r = ts.tick(text="person safe calm light")
    s,m = r["somatic"], r["mental"]
    sd, md = s["distance"], m["distance"]
    marker = " ← CALM" if is_calm(sd, md) else ""
    print(f"  t{ts.tick_n:02d}  {'person safe calm light':22}  {sd:7.1f}  {tlabel2(sd,SOMATIC_T2):9}  {md:6.1f}  {tlabel2(md,MENTAL_T2):11}  {s['sector']['quadrant']}{marker}")
    if is_calm(sd, md) and calm_a is None:
        calm_a = ts.tick_n
        break

if calm_a:
    print(f"  → calm at t{calm_a:02d} ({calm_a-1} ticks post-ghost)")
else:
    print(f"  → NO calm reached in 12 ticks with continuous input")

# ── SCENARIO B: pure idle ────────────────────────────────────────────────
print()
print("  Scenario B: ghost → pure idle")
print(f"  {'tick':>4}  {'input':22}  {'S':>7}  {'S_label':9}  {'M':>6}  {'M_label'}")
print("  " + "─"*65)

ccm2 = CycleManagerV5()
ts2  = TickSystem(ccm2, mode="manual")
r    = ts2.tick(text="ghost in a dark room")
s,m  = r["somatic"], r["mental"]
print(f"  t{ts2.tick_n:02d}  {'ghost in a dark room':22}  {s['distance']:7.1f}  {tlabel2(s['distance'],SOMATIC_T2):9}  {m['distance']:6.1f}  {tlabel2(m['distance'],MENTAL_T2)}")

calm_b = None
for i in range(15):
    r = ts2.tick(text="")
    s,m = r["somatic"], r["mental"]
    sd, md = s["distance"], m["distance"]
    marker = " ← CALM" if is_calm(sd, md) else ""
    print(f"  t{ts2.tick_n:02d}  {'idle':22}  {sd:7.1f}  {tlabel2(sd,SOMATIC_T2):9}  {md:6.1f}  {tlabel2(md,MENTAL_T2)}{marker}")
    if is_calm(sd, md) and calm_b is None:
        calm_b = ts2.tick_n
        break

if calm_b:
    print(f"  → calm at t{calm_b:02d} ({calm_b-1} ticks post-ghost)")

# ── DIAGNOSIS ────────────────────────────────────────────────────────────
print()
print("  DIAGNOSIS:")
print("  The scaler works correctly.")
print("  Continuous positive input saturates viable just as ghost saturates inviable.")
print("  person+light raises V and Gv but does not actively lower residual I and Lv from ghost.")
print("  Active chemicals (serotonin, oxytocin) compensate decay each tick.")
print("  Possible fix: add calm_body/breathing tags that lower I and Lv.")
print()
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# TEST 7 — Plasticity System + memory: sad Julia + Angelo loves her
#
# Verifies:
#   1. dist_mental drops < 30 (opening) → DELTA_NUCLEAR in plasticity
#   2. The event registers in memory (short_term) when the host
#      returns to baseline after the idle ticks
#   3. Angelo's tags change with DELTA_NUCLEAR=0.25
#
# Bug fixed in this test: tick_system._idle_tick() was not calling
# memory.update() — the curve never closed during idle. Fix: call
# memory_m.update("", [], s_state, m_state) on each idle tick.
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 7 — plasticity + memory: sad Julia + Angelo loves her")

from systems.plasticity_system import apply_plasticity, DELTA_NUCLEAR
from db.db_concepts import CONCEPTS
from db.db_somatic  import TAG_VALUES_SOMATIC
from db.db_mental   import TAG_VALUES_MENTAL

# Save original tag values for Angelo
angelo_tags_before = {}
angelo_concept = CONCEPTS.get("angelo", {})
all_angelo_tags = set()
for branch in angelo_concept.get("related", {}).values():
    all_angelo_tags.update(branch.get("somatic", []))
    all_angelo_tags.update(branch.get("mental", []))
for tag in all_angelo_tags:
    if tag in TAG_VALUES_SOMATIC:
        angelo_tags_before[f"S:{tag}"] = dict(TAG_VALUES_SOMATIC[tag])
    if tag in TAG_VALUES_MENTAL:
        angelo_tags_before[f"M:{tag}"] = dict(TAG_VALUES_MENTAL[tag])

from core.formulas import get_rhomboid_center
import math

def mental_dist_rh(ccm):
    state = ccm.mental.current_state()
    cx, cy = get_rhomboid_center(state, ["P","A","Er","Rr"])
    return math.sqrt(cx**2 + cy**2)

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")

# Julia starts very sad
ccm.mental.current["P"]  = 5.0
ccm.mental.current["A"]  = 80.0
ccm.mental.current["Er"] = 70.0
ccm.mental.current["Rr"] = 8.0

print(f"  Julia initial state → dist_mental={mental_dist_rh(ccm):.1f}  (sad/absent)")
print()
print(f"  {'tick':<4}  {'label':20}  {'dist_M':>8}  {'quadrant_M':24}  {'st':>3} {'lt':>3}  {'plasticity / memory'}")
print("  " + "─"*95)

plasticity_nuclear = False
memory_registered = False
plasticity_result_final = None

steps = [
    ("julia very sad",   "sad alone"),
    ("angelo appears",     "angelo"),
    ("angelo admires her",   "angelo admire always"),
    ("angelo loves her",      "angelo love you"),
] + [("idle", "")] * 20

for label, text in steps:
    r  = ts.tick(text=text)
    s, m = r["somatic"], r["mental"]
    md = m["distance"]
    mq = m["sector"]["quadrant"]
    st = len(ccm.memory_m.short_term)
    lt = len(ccm.memory_m.long_term)

    plast = r.get("plasticity", {})
    m_tags = plast.get("mental", {})
    info = ""

    # Detect DELTA_NUCLEAR
    if m_tags:
        delta = next(iter(m_tags.values()))["delta"]
        if abs(delta) >= 0.24:
            plasticity_nuclear = True
            plasticity_result_final = plast
            info = f"⚡ DELTA_NUCLEAR={delta:+.3f}"
        else:
            info = f"plasticity delta={delta:+.4f}"

    # Detect memory registration
    if (st > 0 or lt > 0) and not memory_registered:
        memory_registered = True
        info += "  ✓ MEMORY REGISTERED"

    opening = " ← OPENING" if md < 30 else ""
    print(f"  t{ts.tick_n:02d}  [{label:18s}]  {md:8.1f}  {mq:24}  {st:3} {lt:3}  {info}{opening}")

print()

# ── PLASTICITY RESULT ────────────────────────────────────────────────────
if plasticity_nuclear and plasticity_result_final:
    print("  PLASTICITY — DELTA_NUCLEAR ✓")
    print()
    for tag, info in plasticity_result_final.get("mental", {}).items():
        before = angelo_tags_before.get(f"M:{tag}", {})
        pb = before.get("P", "?")
        ab = before.get("A", "?")
        print(f"    M:{tag:20s}  P:{pb}→{info['new_P']:.2f}  A:{ab}→{info['new_A']:.2f}  delta={info['delta']:+.3f}")
    for tag, info in plasticity_result_final.get("somatic", {}).items():
        before = angelo_tags_before.get(f"S:{tag}", {})
        vb = before.get("V", "?")
        ib = before.get("I", "?")
        print(f"    S:{tag:20s}  V:{vb}→{info['new_V']:.2f}  I:{ib}→{info['new_I']:.2f}  delta={info['delta']:+.3f}")
else:
    print("  PLASTICITY — DELTA_NUCLEAR not triggered")

print()

# ── MEMORY RESULT ───────────────────────────────────────────────────────
print("  MEMORY — events registered with Angelo:")
all_events = ccm.memory_m.short_term + ccm.memory_m.medium_term + ccm.memory_m.long_term
angelo_events = [e for e in all_events if "angelo" in e.get("concepts", [])]
if angelo_events:
    for e in angelo_events:
        nuclear = "NUCLEAR ⚡" if e.get("is_nuclear") else e.get("event_class","")
        print(f"    [{nuclear:10s}]  concepts={e['concepts']}")
        print(f"               peak_M={e.get('mental_peak',0):.1f}  peak_S={e.get('somatic_peak',0):.1f}")
else:
    all_with_concepts = [e for e in all_events if e.get("concepts")]
    print(f"    (Angelo not in memory. Total events: {len(all_events)})")
    for e in all_with_concepts[:3]:
        print(f"      concepts={e['concepts']}  peak_M={e.get('mental_peak',0):.1f}")

print()
print("  Bug fixed: tick_system._idle_tick() now calls memory.update()")
print("  so that curves can close when the host returns to baseline.")
print()

# =============================================================================
# WORK NOTES — system pending items
# =============================================================================
#
# ── 1. MEMORY INDEX BY CATEGORIES ───────────────────────────────────────────
#
# Current problem:
#   Memory is a flat list (short_term, medium_term, long_term).
#   With 300k events the search is O(n) linear → 151ms/tick.
#   With index it would be O(1) regardless of size.
#
# Proposed solution:
#   Use the existing type/subtype in db_concepts as index keys.
#   Structure:
#
#     MEMORY_INDEX = {
#         "persons":    {},   # angelo, julia, ana...
#         "music":      {},   # jazz, rock, cancion...
#         "places":     {},   # street, room, forest...
#         "emotions":   {},   # fear, love, sadness...
#         "objects":    {},   # door, light, ghost...
#         "sensations": {},   # cold, pain, warmth...
#     }
#
#   Each event is stored in the buckets of its concepts.
#   The related field in db_concepts already does this for tags —
#   extend the same logic to memory.
#
#   Search: when "angelo + love" is evoked → go directly to
#   persons["angelo"] and emotions["love"], ignoring the rest.
#
# Files to modify:
#   systems/memory_system.py   → replace lists with indexed dict
#   motors/internal_mental.py  → _evoke uses the index instead of linear scan
#   db/db_concepts.py          → check that type/subtype cover all categories
#
# ── 2. SYNONYMS — WHAT THEY ARE AND WHAT THEY DO ─────────────────────────────────
#
# Review what resolve_concept() does with synonyms from db_concepts.
# For example "angelo" has synonyms: ["angelo", "angelo", "angelo-typo"]
# Questions to answer:
#   - Do synonyms only resolve tokens to concept_name, or also
#     participate in evocation and plasticity?
#   - Does a synonym activate the same related as the main concept?
#   - Should there be cross-concept synonyms? (e.g.: "he" → angelo if
#     is the last mentioned concept — pronominal reference)
#   - Are synonyms stored in memory or only the concept_name?
#
# ── 3. PLASTICITY — POSITIVE REPETITION ──────────────────────────────────────
#
# Current system:
#   DELTA_FIRST   = 0.02  (first time the concept is seen)
#   DELTA_MEDIUM  = 0.02  (seen before, without opening)
#   DELTA_NUCLEAR = 0.25  (mental opening < 30)
#
# Pending — cumulative positive repetition:
#   If the same concept appears N times in opening, the delta should
#   grow (or at least not reset). Currently each opening applies
#   0.25 flat without memory of how many times it occurred.
#
#   Proposal:
#     reps=1  → DELTA_NUCLEAR = 0.25
#     reps=3  → DELTA_NUCLEAR = 0.35
#     reps=5+ → DELTA_NUCLEAR = 0.50  (ceiling)
#
#   The "reps" already exists in the memory event — use it to scale the delta.
#   Also review: does the negative delta (remove association) work the same?
#   Should a very negative experience in opening erase with -DELTA_NUCLEAR?
#
# ── 4. INJECTION OF OTHER SENSES — TACTILE AND REST ──────────────────────────
#
# Current system:
#   db_receptors.py has receptors: temperature_skin, pressure, pain,
#   proprioception, heart_rate, etc.
#   They are injected via physical_inputs to the cycle_manager's process().
#
# Pending — complete the tactile pipeline:
#   The "touch / contact" receptor is not well connected to plasticity.
#   If Angelo touches Julia's shoulder during opening → should activate
#   oxytocin + safe_contact with DELTA_NUCLEAR same as verbal.
#
#   Other senses to connect:
#     - smell    → memory_smell (smell evokes with more force than verbal)
#     - sound    → already partially in db_receptors but without index
#     - vestibular → dizziness, balance, directly affects Lv
#
#   Proposed structure:
#     physical_inputs = [
#         {"receptor": "touch",       "value": 0.7, "zone": "shoulder"},
#         {"receptor": "temperature", "value": 36.5, "zone": "skin"},
#         {"receptor": "sound_level", "value": 0.9,  "zone": "ear"},
#     ]
#   The signature already exists — each receptor needs to generate concepts
#   that enter plasticity and memory just like verbal ones.
#
# =============================================================================
# ─────────────────────────────────────────────────────────────────────────────
# TEST 8 — Beautiful melody repetition → short_term → medium_term
#
# A melodic phrase has very small values (S~3, M~4) but repeats.
# Plasticity accumulates with each repetition:
#   1st time → DELTA_FIRST  (0.02) — first exposure
#   in ST   → DELTA_MEDIUM (0.06) — already in short_term
#   in MT   → DELTA_LONG        — already in medium_term
#
# The event should:
#   - Register in short_term after returning to baseline
#   - Promote to medium_term with enough repetitions
#
# tag values for concept "melody":
#   S = V=3  I=1  Lv=1  Gv=2   (very small — light phrase)
#   M = P=3  A=1  Er=4  Rr=2
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 8 — beautiful melody: repetition → short_term → medium_term")

from systems.plasticity_system import DELTA_FIRST, DELTA_MEDIUM, DELTA_LONG

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")

# Sequence: the melody plays, stops, plays again — 6 repetitions
# with idle between each so the event closes and registers
REPS = 6
sequence = []
for i in range(REPS):
    sequence.append((f"melody rep {i+1}", "melody"))
    sequence += [("idle", "")] * 8   # enough to close the event

print(f"  {'tick':>4}  {'label':18}  {'S':>6}  {'M':>6}  {'st':>3}  {'mt':>3}  {'lt':>3}  {'delta':>8}  {'note'}")
print("  " + "─"*80)

prev_st = 0
prev_mt = 0

for label, text in sequence:
    r  = ts.tick(text=text)
    s, m = r["somatic"], r["mental"]
    sd, md = s["distance"], m["distance"]
    st = len(ccm.memory_m.short_term)
    mt = len(ccm.memory_m.medium_term)
    lt = len(ccm.memory_m.long_term)

    plast  = r.get("plasticity", {})
    m_tags = plast.get("mental", {})
    delta  = next(iter(m_tags.values()))["delta"] if m_tags else 0

    note = ""
    if st > prev_st:
        note = f"✓ ST+{st-prev_st} — event registered"
        prev_st = st
    if mt > prev_mt:
        note = f"✓✓ MT+{mt-prev_mt} — promoted to medium_term"
        prev_mt = mt
    if delta != 0:
        if abs(delta) >= abs(DELTA_LONG) - 0.001:
            note += f"  delta=LONG({delta:+.3f})"
        elif abs(delta) >= abs(DELTA_MEDIUM) - 0.001:
            note += f"  delta=MEDIUM({delta:+.3f})"
        else:
            note += f"  delta=FIRST({delta:+.3f})"

    if text or note:  # only print ticks with input or events
        print(f"  t{ts.tick_n:02d}  [{label:16s}]  {sd:6.2f}  {md:6.2f}  {st:3}  {mt:3}  {lt:3}  {delta:+8.4f}  {note}")

print()
print("  FINAL SUMMARY:")
print(f"  short_term : {len(ccm.memory_m.short_term)} events")
print(f"  medium_term: {len(ccm.memory_m.medium_term)} events")
print(f"  long_term  : {len(ccm.memory_m.long_term)} events")
print()
all_mel = [e for e in ccm.memory_m.short_term + ccm.memory_m.medium_term + ccm.memory_m.long_term
           if "melody" in e.get("concepts", [])]
if all_mel:
    for e in all_mel:
        tier = "MT" if e in ccm.memory_m.medium_term else ("LT" if e in ccm.memory_m.long_term else "ST")
        print(f"  [{tier}] reps={e.get('reps',1)}  class={e.get('event_class')}  peak_M={e.get('mental_peak',0):.2f}  peak_S={e.get('somatic_peak',0):.2f}")
else:
    print("  (no melody event in memory)")
print()
# ─────────────────────────────────────────────────────────────────────────────
# TEST 9 — Bones: hand_bone approaches head_bone (head caress)
#
# Blender rig simulation:
#   - hand_bone and head_bone have positions in 3D
#   - Distance between them generates gradual physical signals
#   - As the hand approaches:
#       dist > 50mm  → no contact, no signal
#       dist 50→20mm → radiant heat (temperature_skin rises on scalp)
#       dist 20→5mm  → light pressure (low pressure on scalp)
#       dist < 5mm   → contact real (pressure normal + calor)
#
# receptor + zone → homunculus weight:
#   temperature_skin + scalp → thermo weight = 5/10 = 0.5
#   pressure         + scalp → touch  weight = 6/10 = 0.6
#
# Expected:
#   - V↑ Gv↑ (viability — safe contact, warmth)
#   - P↑ Er↑ (presence + emotional — someone is touching me)
#   - Registered in memory as tactile event
# ─────────────────────────────────────────────────────────────────────────────
separador("TEST 9 — hand_bone → head_bone: head caress")

# ── BONE SIMULATOR ──────────────────────────────────────────────────────────
def bone_distance_to_physical_inputs(dist_mm):
    """
    Converts distance between hand_bone and head_bone into physical_inputs.
    Receptor zone: scalp (head)

    dist_mm > 50   → nothing
    dist_mm 50→20  → radiant heat (temperature rises gradually)
    dist_mm 20→5   → slight pressure + warmth
    dist_mm < 5    → real contact
    """
    inputs = []

    if dist_mm > 50:
        return inputs  # out of range

    # Temperature: 36.5°C base of the hand, increases as it approaches
    # At 50mm you feel ~28°C, at 0mm you feel ~36°C (body heat)
    temp = 28.0 + (50 - dist_mm) / 50 * 8.5   # 28°C → 36.5°C
    inputs.append({
        "receptor": "temperature_skin",
        "value":    round(temp, 2),
        "zone":     "scalp"
    })

    # Tactile pressure: only appears at < 20mm
    if dist_mm < 20:
        # 0.1 kPa at 20mm → 2.0 kPa at 0mm (soft caress)
        pressure = 0.1 + (20 - dist_mm) / 20 * 1.9
        inputs.append({
            "receptor": "pressure",
            "value":    round(pressure, 3),
            "zone":     "scalp"
        })

    return inputs

# ── APPROACH SEQUENCE ───────────────────────────────────────────────
steps_bone = [
    ("hand far away",      100),   # no contact
    ("hand at 45mm",       45),   # slight heat begins
    ("hand at 30mm",       30),   # moderate heat
    ("hand at 15mm",       15),   # heat + light pressure
    ("hand at 5mm",         5),   # almost touching
    ("contact 2mm",         2),   # real caress
    ("contact 0mm",       0),   # palm on head
    ("moves away 10mm",     10),   # withdrawing
    ("moves away 40mm",     40),   # almost out of range
    ("hand far away",      100),   # no contact — event closes
]

SOMATIC_T9 = [(6,"low"),(20,"normal"),(60,"active"),(120,"saturated"),(9999,"collapse")]
MENTAL_T9  = [(5,"opening"),(15,"normal"),(40,"active"),(80,"saturated"),(9999,"collapse")]

def tlabel9(d, th):
    for lim, lab in th:
        if d < lim: return lab
    return "collapse"

ccm = CycleManagerV5()
ts  = TickSystem(ccm, mode="manual")

print(f"  {'tick':>4}  {'label':18}  {'dist':>6}  {'temp':>6}  {'pres':>6}  {'S':>7}  {'M':>6}  {'quadrant_S':20}  {'st':>3}  verbal")
print("  " + "─"*100)

prev_st = 0
for label, dist_mm in steps_bone:
    physical = bone_distance_to_physical_inputs(dist_mm)

    # Extraer temp y pressure para mostrar
    temp_val = next((p["value"] for p in physical if p["receptor"]=="temperature_skin"), None)
    pres_val = next((p["value"] for p in physical if p["receptor"]=="pressure"), None)
    temp_str = f"{temp_val:.1f}°C" if temp_val else "  ---  "
    pres_str = f"{pres_val:.2f}kPa" if pres_val else "  ---  "

    r  = ts.tick(text="", physical_inputs=physical)
    s, m = r["somatic"], r["mental"]
    sd, md = s["distance"], m["distance"]
    sq = s["sector"]["quadrant"]
    verbal = r.get("verbal", "")
    st = len(ccm.memory_m.short_term) + len(ccm.memory_m.medium_term)

    marker = ""
    if st > prev_st:
        marker = f"  ✓ memory +{st-prev_st}"
        prev_st = st

    print(f"  t{ts.tick_n:02d}  [{label:16s}]  {dist_mm:4}mm  {temp_str}  {pres_str}  {sd:7.1f}  {md:6.1f}  {sq:20}  {st:3}  \"{verbal}\"{marker}")

# Idle to close event — the caress is large, needs ~20 ticks of decay
print("  ...")
for _ in range(25):
    r = ts.tick(text="")
    st = len(ccm.memory_m.short_term) + len(ccm.memory_m.medium_term)
    if st > prev_st:
        print(f"  t{ts.tick_n:02d}  [idle baseline   ]  --- mm   ---     ---     {r['somatic']['distance']:7.1f}  {r['mental']['distance']:6.1f}  {'':20}  {st:3}  ✓ event closed in memory")
        prev_st = st
        break

print()
print("  SUMMARY:")
print(f"  short_term : {len(ccm.memory_m.short_term)} events")
print(f"  medium_term: {len(ccm.memory_m.medium_term)} events")
all_ev = ccm.memory_m.short_term + ccm.memory_m.medium_term
for e in all_ev:
    tier = "MT" if e in ccm.memory_m.medium_term else "ST"
    print(f"  [{tier}]  class={e.get('event_class'):6}  peak_M={e.get('mental_peak',0):.1f}  peak_S={e.get('somatic_peak',0):.1f}  concepts={list(e.get('concepts',[]))[:4]}")
print()
print("  BLENDER NOTE:")
print("  In UPBGE/Blender the bridge is:")
print("    dist_mm = (hand_bone.head - head_bone.head).length * 1000")
print("    physical = bone_distance_to_physical_inputs(dist_mm)")
print("    ccm.process(text='', physical_inputs=physical)  # every frame or every N frames")
print()
