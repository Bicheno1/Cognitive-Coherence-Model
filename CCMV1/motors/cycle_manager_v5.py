# motors/cycle_manager_v5.py — CCM v5
#
# ORCHESTRATOR — coordinates the 4 motors in sequence
#
# FULL FLOW:
#
#  SOMATIC EXTERNAL ←ping-pong→ MENTAL EXTERNAL
#         ↓                            ↓
#   somatic_engine              mental_engine
#         ↓     ←cross-recal→         ↓
#              state (D, C)
#                   ↑↓
#  SOMATIC INTERNAL    MENTAL INTERNAL
#  (reflexes, vital)   (evocation, reflexes)
#         ↓                    ↓
#    amplifies/contains the state
#         ↓
#    story_modifier learns
#    memory registers
#    output_checker decides which dominates

from engines.somatic_engine import SomaticEngine
from engines.mental_engine   import MentalEngine
from systems.memory_system   import MemorySystem
from systems.chemical_system     import ChemicalSystem
from systems.mental_state_system import MentalStateSystem
from systems.perception_system import PerceptionSystem

from motors.external_somatic import process as ext_somatic_process, from_perception
from motors.external_mental  import process as ext_mental_process, resolve_text
from motors.internal_somatic import process as int_somatic_process
from motors.internal_mental  import process as int_mental_process
from motors.vitality_stats   import VitalityStats
from motors.mind_stats       import MindStats
from motors.core_identity    import consult as core_consult, apply as core_apply

from db.db_somatic import SOMATIC_KEYS
from db.db_mental  import MENTAL_KEYS
from layers.quadrant_reader import read_somatic_sector, read_mental_sector
from layers.emotion_mapper  import get_emotion, get_somatic_state
from layers.processing_mode import get_processing_mode
from systems.plasticity_system import apply_plasticity
from core.formulas import calculate_D, calculate_C, calculate_df
import math


def _get_processing_mode_info(cfx: float, m_dist: float) -> dict:
    """Helper — derives tension label and calls get_processing_mode."""
    from output.output_layer import get_tension_mental
    tension = get_tension_mental(m_dist)
    return get_processing_mode(cfx, tension)

class CycleManagerV5:
    def __init__(self):
        # Motores de state
        self.somatic    = SomaticEngine()
        self.mental     = MentalEngine()

        # Sistemas de stats
        self.vitality   = VitalityStats()
        self.mind       = MindStats()

        # Separate memories (somatic and mental)
        self.memory_s   = MemorySystem()
        self.memory_m   = MemorySystem()

        # Chemicals (complementary somatic internal)
        self.chemicals     = ChemicalSystem()

        # mental states (complementary mental internal)
        self.mental_states = MentalStateSystem()

        # Perception (Blender)
        self.perception = PerceptionSystem()

        self._last_concepts = []

    # ──────────────────────────────────────────────
    # MAIN CYCLE
    # ──────────────────────────────────────────────

    def process(self, text: str = "", physical_inputs: list = None) -> dict:
        """
        Main entry point.

        text            : input vocal/textual
        physical_inputs : list of physical signals from the rig
                          [{"receptor": "temperature_skin", "value": 33.0, "zone": "face"}]
        """
        physical_inputs = physical_inputs or []

        # ── STEP 1: EXTERNAL MOTORS ────────────────────────────
        # Resolve concepts from text first
        from db.db_concepts import resolve_concept
        STOPWORDS = {"a","an","the","in","on","at","is","are","was","i","and","or","of"}
        tokens = [t for t in text.lower().split() if t not in STOPWORDS] if text else []
        concept_names = []
        for token in tokens:
            name = resolve_concept(token)
            if name and name not in concept_names:
                concept_names.append(name)

        # Blender Perception
        scan = self.perception.scan()
        perception_physical  = from_perception(scan)
        perception_concepts  = self.perception.get_concepts()
        all_physical = physical_inputs + perception_physical
        for c in perception_concepts:
            if c not in concept_names:
                concept_names.append(c)

        self._last_concepts = concept_names

        # Pre-input semantic → vectors for both external motors
        from core.pre_input import pre_input_somatic, pre_input_mental
        vec_s_semantic = pre_input_somatic(concept_names, memory=self.memory_s) if concept_names else None
        vec_m          = pre_input_mental(concept_names,  memory=self.memory_m) if concept_names else None

        # Physical pre-input → somatic external (rig signals)
        vec_s_physical = ext_somatic_process(all_physical)

        # Combine both somatic vectors
        if vec_s_semantic and vec_s_physical:
            vec_s = {k: vec_s_semantic[k] + vec_s_physical[k] for k in SOMATIC_KEYS}
            vec_s["_pipeline"] = "external_somatic+semantic"
        elif vec_s_semantic:
            vec_s = vec_s_semantic
        else:
            vec_s = vec_s_physical

        # Internal activations from the graph → chemicals
        from db.db_concepts import get_internal_activations
        somatic_acts, mental_acts = get_internal_activations(concept_names) if concept_names else ({}, {})

        # ── STEP 1.5: TAG SCALER ──────────────────────────────
        # Scales the vector according to current engine distance.
        # If the host is already tense → new input hits harder.
        # Simulates intoxication, trauma, altered states.
        from layers.tag_scaler import scale_tag
        from core.formulas import get_rhomboid_center
        import math
        if vec_s:
            s = self.somatic.current_state()
            scx, scy = get_rhomboid_center(s, SOMATIC_KEYS)
            s_dist = math.sqrt(scx**2 + scy**2)
            vec_s = scale_tag(vec_s, s_dist, SOMATIC_KEYS)
        if vec_m:
            m = self.mental.current_state()
            mcx, mcy = get_rhomboid_center(m, MENTAL_KEYS)
            m_dist = math.sqrt(mcx**2 + mcy**2)
            vec_m = scale_tag(vec_m, m_dist, MENTAL_KEYS)

        # ── step 2: CORE IDENTITY filtra vectores externos ─────
        core_active = core_consult(concept_names) if concept_names else []

        if vec_s and core_active:
            vec_s = core_apply(vec_s, SOMATIC_KEYS, core_active)
        if vec_m and core_active:
            vec_m = core_apply(vec_m, MENTAL_KEYS, core_active)

        # ── step 3: VITALITY TICK ──────────────────────────────
        self.vitality.tick(active_concepts=concept_names)
        vital_s, vital_m = self.vitality.get_pressure()

        # ── STEP 4: CHEMICALS + MENTAL STATES ────────────────────
        # Direct triggers per concept + graph multiplier
        self.chemicals.process_triggers(concept_names, vitality_stats=self.vitality.all_needs())
        # Apply graph multipliers (adrenaline x2 → extra release)
        for tag, count in somatic_acts.items():
            if count > 1:
                self.chemicals.release(tag, amount=count - 1)
        chem_s = self.chemicals.get_somatic_push()

        # Mental states — mental analog of the chemicals
        self.mental_states.process_triggers(concept_names)
        chem_m = self.mental_states.get_mental_push()

        # ── STEP 5: STATE BEFORE (for plasticity) ─────────────
        state_before_s = dict(self.somatic.current_state())
        state_before_m = dict(self.mental.current_state())

        # ── STEP 6: PING-PONG EXTERNAL ──────────────────────────
        # Ping 1 — somatic receives external + internal pressure
        if vec_s:
            self.somatic.apply_external(vec_s)
        self.somatic.apply_internal(vital_s)
        self.somatic.apply_internal(chem_s)
        D1 = self.somatic.D()   # direct somatic impact

        # Ping 2 — mental receives external + D1 (cross)
        if vec_m:
            self.mental.apply_external(vec_m)
        self.mental.apply_internal(vital_m)
        self.mental.apply_internal(chem_m)
        self.mental.recalibrate(D1)
        C1 = self.mental.C()    # direct mental impact

        # Pong — somatic receives C1
        self.somatic.recalibrate(C1)
        D2 = self.somatic.D()   # direct somatic impact post-cross

        # Ping final — mental receives D2
        self.mental.recalibrate(D2)
        C2 = self.mental.C()    # direct mental impact post-cross

        # ── STEP 6.5: HOMEOSTATIC DECAY ────────────────
        dx2, dy2 = D2
        cx2, cy2 = C2
        s_intensity = math.sqrt(dx2**2 + dy2**2) / 100.0
        m_intensity = math.sqrt(cx2**2 + cy2**2) / 100.0
        decay_s = max(0.05, 0.20 - s_intensity * 0.10)
        decay_m = max(0.05, 0.20 - m_intensity * 0.10)
        self.somatic.decay_toward_base(rate=decay_s)
        self.mental.decay_toward_base(rate=decay_m)

        # ── STEP 7: INTERNAL MOTORS ────────────────────────────
        int_s = int_somatic_process(D2, self.vitality.all_needs(), chemical_system=self.chemicals)
        self.somatic.apply_internal(int_s)
        int_m = int_mental_process(chem_m)
        self.mental.apply_internal(int_m)

        # ── STEP 7.5: FINAL IMPACT (Df / Cf) ────────────────
        # D1/C1 = direct impact     — the raw hit
        # D2/C2 = relational impact — how it distributes across factors
        # Df/Cf = final impact      — median point D1↔D2, dampens without losing direction
        s_state_final = self.somatic.current_state()
        m_state_final = self.mental.current_state()
        Df = calculate_df(s_state_final, ["V", "I", "Lv", "Gv"])
        Cf = calculate_df(m_state_final, ["P", "A", "Er", "Rr"])

        # Chemicals + mental states decay
        self.chemicals.decay()
        self.mental_states.decay()

        # ── step 8: MIND STATS tick ────────────────────────────
        self.mind.tick()

        # ── STEP 9: STORY MODIFIER (plasticity) ────────────────
        plasticity = {}
        if concept_names:
            state_after_s = dict(self.somatic.current_state())
            state_after_m = dict(self.mental.current_state())
            state_after_m_tmp = dict(self.mental.current_state())
            from core.formulas import get_rhomboid_center as _grc
            import math as _math
            _cx, _cy = _grc(state_after_m_tmp, ["P","A","Er","Rr"])
            _dist_mental_now = _math.sqrt(_cx**2 + _cy**2)
            plasticity = apply_plasticity(
                concept_names, self.memory_m,
                state_before_s, state_after_s,
                state_before_m, state_after_m,
                dist_mental=_dist_mental_now,
            )

        # ── STEP 10: MEMORY ───────────────────────────────────
        s_state = self.somatic.current_state()
        m_state = self.mental.current_state()

        self.memory_s.update(text, concept_names, s_state, m_state)
        self.memory_m.update(text, concept_names, s_state, m_state)

        # ── STEP 11: OUTPUT ────────────────────────────────────
        return self._build_output(
            Df, Cf, D1, C1, core_active,
            int_s, int_m, plasticity
        )

    # ──────────────────────────────────────────────
    # OUTPUT
    # ──────────────────────────────────────────────

    def _build_output(self, Df, Cf, D1, C1, core_active, int_s, int_m, plasticity):
        s_state = self.somatic.current_state()
        m_state = self.mental.current_state()

        # Df y Cf son (cx, cy) — impact final
        dfx, dfy = Df
        cfx, cfy = Cf
        d1x, d1y = D1
        c1x, c1y = C1

        s_dist = math.sqrt(dfx**2 + dfy**2)
        m_dist = math.sqrt(cfx**2 + cfy**2)

        dominant = "somatic" if s_dist >= m_dist else "mental"

        # Muscle tone — X-axis dominance drives tension/relaxation
        from layers.muscle_tone import apply_muscle_tone
        muscle_tone = apply_muscle_tone(dfx, s_dist, cfx, m_dist)

        # Scalar display — distance with sign of cy
        Df_display = math.copysign(s_dist, dfy)
        Cf_display = math.copysign(m_dist, cfy)
        D1_display = math.copysign(math.sqrt(d1x**2 + d1y**2), d1y)
        C1_display = math.copysign(math.sqrt(c1x**2 + c1y**2), c1y)

        # Verbal output — two independent channels
        from output.output_layer import get_verbal_somatic, get_verbal_mental
        from output.phrase_builder import build_phrase
        verbal_s = get_verbal_somatic(s_state, s_dist, chemical_levels=self.chemicals.levels)
        verbal_m = get_verbal_mental(m_state, m_dist)

        # Phrase builder — responds if there is a question and dist_mental < 90
        phrase = build_phrase(
            active_concepts = self._last_concepts,
            core_rules      = core_active,
            dist_mental     = m_dist,
        )

        # Processing-mode reactive phrase — fallback when no identity/question matched
        if not phrase and dominant == "mental":
            from output.phrase_builder import build_reactive_phrase
            from output.output_layer import get_tension_mental
            m_tension = get_tension_mental(m_dist)
            m_quadrant = read_mental_sector(m_state).get("quadrant", "present-rational")
            phrase = build_reactive_phrase(
                active_concepts = self._last_concepts,
                cfx             = cfx,
                tension         = m_tension,
                quadrant        = m_quadrant,
                dist_mental     = m_dist,
            )

        verbal = phrase if phrase else (verbal_s if dominant == "somatic" else verbal_m)

        return {
            "dominant":    dominant,
            "verbal":      verbal,
            "verbal_s":    verbal_s,
            "verbal_m":    verbal_m,
            "somatic": {
                "state":    s_state,
                "D1":       round(D1_display, 4),
                "Df":       round(Df_display, 4),
                "distance": round(s_dist, 4),
                "sector":   read_somatic_sector(s_state),
                "emotion":  get_somatic_state(dfx, dfy, chemical_levels=self.chemicals.levels),
                "internal": int_s.get("_active", []),
                "_int_s": int_s,
                "muscle_tone": muscle_tone,
            },
            "mental": {
                "state":    m_state,
                "C1":       round(C1_display, 4),
                "Cf":       round(Cf_display, 4),
                "distance": round(m_dist, 4),
                "sector":   read_mental_sector(m_state),
                "emotion":  get_emotion(cfx, cfy, mental_state_levels=self.mental_states.levels),
                "internal": int_m.get("_active", []),
                "evoked":   int_m.get("_evoked", []),
                "processing": _get_processing_mode_info(cfx, m_dist),
            },
            "core_active":   [r[0] for r in core_active],
            "vitality":      self.vitality.status(),
            "core_status":   self.vitality.core_status(),
            "mind_stats":    self.mind.status(),
            "chemicals":     self.chemicals.status(),
            "mental_states": self.mental_states.status(),
            "memory_s":      self.memory_s.summary(),
            "memory_m":      self.memory_m.summary(),
            "concepts":      self._last_concepts,
            "_core_rules":   core_active,
            "_chemicals":    self.chemicals.levels,
            "plasticity":    plasticity,
        }
