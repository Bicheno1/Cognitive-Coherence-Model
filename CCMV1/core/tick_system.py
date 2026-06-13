# core/tick_system.py — CCM v5
#
# TICK SYSTEM — unidad de tiempo of the host
#
# 1 tick = 2 seconds = average of one sentence
#
# Each tick the system runs even if there is no external input:
#   - chemicals decaen (half_life individual)
#   - vitality decays hacia baseline
#   - mind_stats decays hacia baseline
#   - memory context_window acumula cycles
#   - si hay input → procesa cycle completo
#   - si no hay input → solo decay internal
#
# MODOS:
#   REALTIME  — usa time.sleep(2.0), corre en thread
#   MANUAL    — tick() llamado desde fuera (Blender, tests, etc.)
#   STEPPED   — N ticks at once (simulation, training)

import time
import threading

TICK_SECONDS = 2.0   # duration of one tick


class TickSystem:
    def __init__(self, cycle_manager, mode="manual"):
        """
        cycle_manager : CycleManagerV5 instance
        mode          : "realtime" | "manual" | "stepped"
        """
        self.cm        = cycle_manager
        self.mode      = mode
        self.tick_n    = 0          # contador de ticks
        self.running   = False
        self._thread   = None
        self._pending_input = None  # input waiting for the next tick

    # ── PUBLIC API ───────────────────────────────────────────────────────────

    def start(self):
        """Starts the real-time loop (realtime mode only)."""
        if self.mode != "realtime":
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def queue_input(self, text="", physical_inputs=None):
        """Queues an input for the next tick."""
        self._pending_input = {
            "text":            text,
            "physical_inputs": physical_inputs or [],
        }

    def tick(self, text="", physical_inputs=None):
        """
        Ejecuta un tick manualmente.
        If text or physical_inputs are provided, processes them.
        If not, only runs internal decay.
        """
        self.tick_n += 1

        has_input = bool(text or physical_inputs)

        if has_input:
            result = self.cm.process(text=text, physical_inputs=physical_inputs or [])
        else:
            result = self._idle_tick()

        result["tick"]     = self.tick_n
        result["has_input"] = has_input
        return result

    def stepped(self, n, text="", physical_inputs=None):
        """
        Corre N ticks.
        Input is only applied on the first tick; the rest are idle.
        Useful for simulating the passage of time after an event.
        """
        results = []
        for i in range(n):
            if i == 0:
                r = self.tick(text=text, physical_inputs=physical_inputs)
            else:
                r = self.tick()
            results.append(r)
        return results

    # ── IDLE TICK — no external input ────────────────────────────────────────

    def _idle_tick(self):
        """
        Tick without input — internal decay only.
        The host stays alive: chemicals drop, needs drop,
        mind_stats decae, context_window acumula.
        """
        # Decay de chemicals
        self.cm.chemicals.decay()

        # Vitality tick (decay de needs)
        self.cm.vitality.tick(active_concepts=[])

        # Mind stats tick
        self.cm.mind.tick()

        # Homeostatic decay of current state
        self.cm.somatic.decay_toward_base(rate=0.15)
        self.cm.mental.decay_toward_base(rate=0.15)

        # Context window — evaluate if the curve closed at baseline
        s_state = self.cm.somatic.current_state()
        m_state = self.cm.mental.current_state()
        self.cm.memory_s.update("", [], s_state, m_state)
        self.cm.memory_m.update("", [], s_state, m_state)

        return self._build_idle_output()

    def _build_idle_output(self):
        import math
        from layers.quadrant_reader import read_somatic_sector, read_mental_sector

        s = self.cm.somatic.current_state()
        m = self.cm.mental.current_state()

        sx = s["Lv"] - s["Gv"]
        sy = s["V"]  - s["I"]
        mx = m["Er"] - m["Rr"]
        my = m["P"]  - m["A"]

        s_dist = math.sqrt(sx**2 + sy**2)
        m_dist = math.sqrt(mx**2 + my**2)

        return {
            "dominant":   "somatic" if s_dist >= m_dist else "mental",
            "somatic":    {"state": s, "distance": round(s_dist, 4), "sector": read_somatic_sector(s)},
            "mental":     {"state": m, "distance": round(m_dist, 4), "sector": read_mental_sector(m)},
            "chemicals":  self.cm.chemicals.status(),
            "vitality":   self.cm.vitality.status(),
            "mind_stats": self.cm.mind.status(),
            "concepts":   [],
            "idle":       True,
        }

    # ── LOOP REALTIME ─────────────────────────────────────────────────────────

    def _loop(self):
        while self.running:
            start = time.time()

            pending = self._pending_input
            self._pending_input = None

            if pending:
                self.tick(text=pending["text"], physical_inputs=pending["physical_inputs"])
            else:
                self._idle_tick()
                self.tick_n += 1

            elapsed = time.time() - start
            sleep_t = max(0.0, TICK_SECONDS - elapsed)
            time.sleep(sleep_t)

    # ── STATUS ────────────────────────────────────────────────────────────────

    def status(self):
        return {
            "tick_n":       self.tick_n,
            "mode":         self.mode,
            "running":      self.running,
            "tick_seconds": TICK_SECONDS,
            "pending_input": self._pending_input is not None,
        }
