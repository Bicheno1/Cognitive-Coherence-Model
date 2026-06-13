# systems/memory_system.py — CCM v4
#
# MEMORY ARCHITECTURE
# ═══════════════════
#
# CONTEXT WINDOW — active input being processed right now.
#   Accumulates concepts each cycle. Detects events by curve shape:
#   baseline → peak → return to baseline. Each complete curve = one event.
#   Events are classified by peak height (mental scale 0–200, somatic scale 0–400).
#
# EVENT CLASSIFICATION
#   mental:   0–8 micro  |  8–50 medium  |  50–90 large  |  90+ major
#   somatic:  0–6 micro  |  6–100 medium  |  100–180 large  |  180+ major
#
# EVENT GRAPH — 3 key points (bezier-like curve):
#   start: (D, C) at baseline before event
#   peak:  (D, C) at maximum activation
#   end:   (D, C) after returning toward baseline
#
# SHORT TERM — last N events. Each: event text + graph.
#   Capacity: 10. Age out after 10 cycles with no reinforcement.
#
# MEDIUM TERM — compressed events. Promoted from short term by repetition (3x).
#   Stores reduced concept list + compressed graph.
#   Capacity: 100. Fades after ~100 cycles.
#
# LONG TERM — significant events. Two promotion paths:
#   1. Repetition: medium term event seen 10x.
#   2. High activation: major event that self-regulated back to baseline.
#   Capacity: 100. nuclear events never deleted.
#
# CORE (nuclear) — personality-defining events.
#   System was in critical state AND self-regulated back to near-center.

import math

# ── THRESHOLDS ────────────────────────────────────────────────────────────────
# Euclidean distances to center for event classification
# mental  (vars 0-200): micro<8   medium<50  large<90  major>=170
# somatic (vars 0-400): micro<6   medium<100 large<180 major>=340
# micro lowered to 8/6 to capture soft events (melody, whisper, breeze)

MENTAL_MICRO  = 8     # was 20 — lowered to capture soft events
MENTAL_MEDIUM = 50
MENTAL_LARGE  = 90
MENTAL_MAJOR  = 170

SOMATIC_MICRO  = 6    # was 40 — lowered to capture soft events
SOMATIC_MEDIUM = 100
SOMATIC_LARGE  = 180
SOMATIC_MAJOR  = 340

BASELINE_THRESHOLD     = 11     # real neutral state C~9.2 — closes event when host returns to rest
HIGH_MENTAL_THRESHOLD  = 90     # high mental distance
HIGH_SOMATIC_THRESHOLD = 180    # high somatic distance
NUCLEAR_THRESHOLD      = 10     # near-center threshold to mark nuclear

SHORT_TERM_MAX  = 10
MEDIUM_TERM_MAX = 100
LONG_TERM_MAX   = 100

SHORT_TERM_AGE  = 10
MEDIUM_TERM_AGE = 100

SHORT_TO_MEDIUM_REPS = 3
MEDIUM_TO_LONG_REPS  = 10

EVENT_START_MENTAL  = 10    # was 20 — lowered for soft events (melody, breeze)
EVENT_START_SOMATIC = 8     # was 40

# ── HELPERS ───────────────────────────────────────────────────────────────────

def _mental_dist(s):
    mx = s.get("Er", 0.0) - s.get("Rr", 0.0)
    my = s.get("P",  0.0) - s.get("A",  0.0)
    return math.sqrt(mx**2 + my**2)

def _somatic_dist(s):
    sx = s.get("Lv", 0.0) - s.get("Gv", 0.0)
    sy = s.get("V",  0.0) - s.get("I",  0.0)
    return math.sqrt(sx**2 + sy**2)

def _classify(mental_peak, somatic_peak):
    if mental_peak >= MENTAL_MAJOR  or somatic_peak >= SOMATIC_MAJOR:  return "major"
    if mental_peak >= MENTAL_LARGE  or somatic_peak >= SOMATIC_LARGE:  return "large"
    if mental_peak >= MENTAL_MEDIUM or somatic_peak >= SOMATIC_MEDIUM: return "medium"
    if mental_peak >= MENTAL_MICRO  or somatic_peak >= SOMATIC_MICRO:  return "micro"
    return None

def _key(concepts, n=5):
    seen = []
    for c in concepts:
        if c not in seen: seen.append(c)
    return seen[:n]

def _compress(concepts, n=3):
    seen = []
    for c in concepts:
        if c not in seen: seen.append(c)
    return seen[:n]

# ── MEMORY SYSTEM ─────────────────────────────────────────────────────────────

class MemorySystem:
    def __init__(self):
        # Context window state
        self._ctx_concepts   = []
        self._ctx_start      = None
        self._ctx_peak_D     = 0.0
        self._ctx_peak_C     = 0.0
        self._ctx_active     = False
        self._ctx_cycle      = 0

        self.short_term  = []
        self.medium_term = []
        self.long_term   = []
        self._cycle      = 0

    # ── MAIN UPDATE ───────────────────────────────────────────────────────────

    def update(self, text, concepts, somatic_state, mental_state):
        self._cycle += 1
        D = _somatic_dist(somatic_state)
        C = _mental_dist(mental_state)
        self._age_memories()
        event = self._track_curve(text, concepts, D, C, somatic_state, mental_state)
        if event:
            self._promote(event)
        return event

    # ── CURVE TRACKING ────────────────────────────────────────────────────────

    def _track_curve(self, text, concepts, D, C, somatic_state, mental_state):
        at_baseline = C < BASELINE_THRESHOLD and D < BASELINE_THRESHOLD * 2

        if not self._ctx_active:
            if C >= EVENT_START_MENTAL or D >= EVENT_START_SOMATIC:
                self._ctx_active   = True
                self._ctx_concepts = list(concepts)
                self._ctx_start    = (round(D, 4), round(C, 4))
                self._ctx_peak_D   = D
                self._ctx_peak_C   = C
                self._ctx_cycle    = 1
        else:
            self._ctx_cycle += 1
            for c in concepts:
                if c not in self._ctx_concepts:
                    self._ctx_concepts.append(c)
            if D > self._ctx_peak_D: self._ctx_peak_D = D
            if C > self._ctx_peak_C: self._ctx_peak_C = C

            if at_baseline and self._ctx_cycle >= 2:
                event = self._close_event(text, D, C, somatic_state, mental_state)
                self._reset_ctx()
                return event
        return None

    def _close_event(self, text, end_D, end_C, somatic_end, mental_end):
        ec = _classify(self._ctx_peak_C, self._ctx_peak_D)
        if not ec:
            return None

        graph = {
            "start": self._ctx_start,
            "peak":  (round(self._ctx_peak_D, 4), round(self._ctx_peak_C, 4)),
            "end":   (round(end_D, 4), round(end_C, 4)),
        }

        is_nuclear = (
            (self._ctx_peak_C >= HIGH_MENTAL_THRESHOLD or
             self._ctx_peak_D >= HIGH_SOMATIC_THRESHOLD) and
            end_D < BASELINE_THRESHOLD * 2 and
            end_C < NUCLEAR_THRESHOLD
        )

        return {
            "text":         text,
            "concepts":     _key(self._ctx_concepts),
            "graph":        graph,
            "event_class":  ec,
            "is_nuclear":   is_nuclear,
            "mental_peak":  round(self._ctx_peak_C, 4),
            "somatic_peak": round(self._ctx_peak_D, 4),
            "age":          0,
            "reps":         1,
        }

    def _reset_ctx(self):
        self._ctx_concepts = []
        self._ctx_start    = None
        self._ctx_peak_D   = 0.0
        self._ctx_peak_C   = 0.0
        self._ctx_active   = False
        self._ctx_cycle    = 0

    # ── PROMOTION ─────────────────────────────────────────────────────────────

    def _promote(self, event):
        if not event:
            return
        if event["is_nuclear"] or event["event_class"] == "major":
            self._add_long(event)
            return

        existing_s = self._find(self.short_term, event["concepts"])
        if existing_s:
            existing_s["reps"] += 1
            existing_s["age"]   = 0
            if existing_s["reps"] >= SHORT_TO_MEDIUM_REPS:
                self._add_medium(existing_s)
            return

        self._add_short(event)

        if event["event_class"] == "large":
            existing_m = self._find(self.medium_term, event["concepts"])
            if existing_m:
                existing_m["reps"] += 1
                existing_m["age"]   = 0
                if existing_m["reps"] >= MEDIUM_TO_LONG_REPS:
                    self._add_long(existing_m)

    def _find(self, memory_list, concepts):
        cs = set(concepts)
        for entry in memory_list:
            overlap = cs & set(entry.get("concepts", []))
            if len(overlap) >= max(1, len(cs) // 2):
                return entry
        return None

    def _add_short(self, event):
        self.short_term.append({
            "text":         event["text"],
            "concepts":     _key(event["concepts"]),
            "graph":        event["graph"],
            "event_class":  event["event_class"],
            "is_nuclear":   event["is_nuclear"],
            "mental_peak":  event["mental_peak"],
            "somatic_peak": event["somatic_peak"],
            "age": 0, "reps": 1,
        })
        if len(self.short_term) > SHORT_TERM_MAX:
            non = [e for e in self.short_term if not e["is_nuclear"]]
            nuc = [e for e in self.short_term if e["is_nuclear"]]
            self.short_term = nuc + non[-(SHORT_TERM_MAX - len(nuc)):]

    def _add_medium(self, event):
        entry = {
            "concepts":     _compress(event["concepts"]),
            "graph":        event["graph"],
            "event_class":  event["event_class"],
            "is_nuclear":   event["is_nuclear"],
            "mental_peak":  event["mental_peak"],
            "somatic_peak": event["somatic_peak"],
            "age": 0, "reps": event.get("reps", 1),
        }
        if not self._find(self.medium_term, entry["concepts"]):
            self.medium_term.append(entry)
        if len(self.medium_term) > MEDIUM_TERM_MAX:
            non = [e for e in self.medium_term if not e["is_nuclear"]]
            nuc = [e for e in self.medium_term if e["is_nuclear"]]
            self.medium_term = nuc + non[-(MEDIUM_TERM_MAX - len(nuc)):]

    def _add_long(self, event):
        entry = {
            "concepts":     _compress(event["concepts"], n=4),
            "graph":        event["graph"],
            "event_class":  event["event_class"],
            "is_nuclear":   event["is_nuclear"],
            "mental_peak":  event["mental_peak"],
            "somatic_peak": event["somatic_peak"],
            "reps":         event.get("reps", 1),
        }
        self.long_term.append(entry)
        if len(self.long_term) > LONG_TERM_MAX:
            non = [e for e in self.long_term if not e["is_nuclear"]]
            nuc = [e for e in self.long_term if e["is_nuclear"]]
            self.long_term = nuc + non[-(LONG_TERM_MAX - len(nuc)):]

    # ── AGING ─────────────────────────────────────────────────────────────────

    def _age_memories(self):
        for e in self.short_term:  e["age"] += 1
        for e in self.medium_term: e["age"] += 1
        self.short_term  = [e for e in self.short_term  if e["is_nuclear"] or e["age"] < SHORT_TERM_AGE]
        self.medium_term = [e for e in self.medium_term if e["is_nuclear"] or e["age"] < MEDIUM_TERM_AGE]

    # ── EVOCATION ─────────────────────────────────────────────────────────────

    def evoke(self, current_concepts, current_distance):
        if not self.long_term:
            return []
        evoked = []
        cs = set(current_concepts)
        for event in self.long_term:
            if not (cs & set(event.get("concepts", []))):
                continue
            pD, pC = event["graph"]["peak"]
            peak_dist = math.sqrt(pD**2 + pC**2)
            # threshold relativo: 40% of peak distance, minimum 5
            threshold = max(5.0, peak_dist * 0.40)
            if abs(peak_dist - current_distance) <= threshold:
                evoked.append(event)
        return evoked

    # ── STATUS ────────────────────────────────────────────────────────────────

    def context_status(self):
        return {
            "active":   self._ctx_active,
            "concepts": self._ctx_concepts,
            "start":    self._ctx_start,
            "peak":     (round(self._ctx_peak_D, 4), round(self._ctx_peak_C, 4)),
            "cycle":    self._ctx_cycle,
        }

    def summary(self):
        nuc = [e for e in self.long_term if e["is_nuclear"]]
        return {
            "context_active":   self._ctx_active,
            "short_term_size":  len(self.short_term),
            "short_term_last":  self.short_term[-3:] if self.short_term else [],
            "medium_term_size": len(self.medium_term),
            "long_term_total":  len(self.long_term),
            "nuclear_total":    len(nuc),
        }

    def get_context(self):
        return {
            "context_window": self.context_status(),
            "short_term":     self.short_term,
            "medium_term":    self.medium_term,
            "long_term":      self.long_term,
        }

    # ── LEGACY STUBS ──────────────────────────────────────────────────────────

    def update_short_term(self, text): pass
    def update_medium_term(self, concepts): pass
    def track_state(self, distance, concepts, somatic_state, mental_state): pass
    def try_record_long_term(self, current_distance, somatic_state, mental_state, concepts): return None
