# agent.py
# CCM — Main host entry point
# Usage: python agent.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motors.cycle_manager_v5 import CycleManagerV5 as CycleManager
from output.output_layer import generate_output


def print_state(state, verbose=False):
    s = state["somatic"]
    m = state["mental"]

    print("\n" + "="*55)
    print(f"  SOMATIC ENGINE   D={s['D']:+.4f}   [{s['tension'].upper()}]")
    print(f"  {'─'*51}")
    print(f"  Point: x={s['x']:+.3f}  y={s['y']:+.3f}   dist={s['distance']:.3f}")
    print(f"  Quadrant: {s['sector']['quadrant'].upper()}")
    if s.get("muscle_tone"):
        mt = s["muscle_tone"]
        dom = mt["dominant_motor"]
        sig = mt["somatic_signal"] if dom == "somatic" else mt["mental_signal"]
        print(f"  Muscle:   {mt['direction'].upper():<12}  {mt['muscle_tension']:.1f}% MVC  [{mt['label']}]  via {dom}")
    if verbose:
        st = s['state']
        print(f"  V={st['V']:.3f}  I={st['I']:.3f}  Lv={st['Lv']:.3f}  Gv={st['Gv']:.3f}")
        print(f"  ext: V={s['external']['V']:.3f} I={s['external']['I']:.3f}")
        print(f"  int: V={s['internal']['V']:.3f} I={s['internal']['I']:.3f}")

    print(f"\n  MENTAL ENGINE    C={m['C']:+.4f}   [{m['tension'].upper()}]")
    print(f"  {'─'*51}")
    print(f"  Point: x={m['x']:+.3f}  y={m['y']:+.3f}   dist={m['distance']:.3f}")
    print(f"  Quadrant: {m['sector']['quadrant'].upper()}")
    if m.get("processing"):
        pm = m["processing"]
        print(f"  Processing: {pm['processing_mode'].upper()}   depth={pm['inference_depth']}   {'[PREVERBAL]' if pm['preverbal'] else ''}")
    if verbose:
        st = m['state']
        print(f"  P={st['P']:.3f}  A={st['A']:.3f}  Er={st['Er']:.3f}  Rr={st['Rr']:.3f}")

    print(f"\n  Active scene: {state['scene_concepts']}")

    if state.get("evoked"):
        for e in state["evoked"]:
            tag = "NUCLEAR" if e["is_nuclear"] else "memory"
            print(f"  ↑ Evoked [{tag}]: {e['concepts']}")

    if state.get("recorded"):
        r = state["recorded"]
        tag = "NUCLEAR" if r["is_nuclear"] else "long term"
        print(f"  ✦ Recorded [{tag}]: {r['concepts']}")

    out = generate_output(state, core_active_rules=state.get("_core_rules", []))
    print(f"\n  ── OUTPUT {'SOMATIC' if out['dominant']=='corporal' else 'MENTAL'} DOMINATES ──")
    print(f"  Verbal:    \"{out['verbal']}\"")
    print(f"  Movement:  {out['movement']['steps']}")
    print(f"  Speed:     {out['movement']['speed']}x")

    if verbose and state.get("memory"):
        mem = state["memory"]
        print(f"\n  Memory — short: '{mem['short_term'][:40]}...'")
        print(f"  Medium: {mem['medium_term_last']}")
        print(f"  Long: {mem['long_term_total']} events ({mem['nuclear_total']} nuclear)")

    print("="*55)


def run_interactive(use_viz=False):
    ccm = CycleManager()
    viz = None

    if use_viz:
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            from visualizer import CCMVisualizer
            viz = CCMVisualizer(ccm)
            viz.show()
            print("  Visualizer active.")
        except Exception as e:
            print(f"  Visualizer unavailable: {e}")

    print("\n  CCM — Cognitive Coherence Model")
    print("  Type a scene in English. 'q' to quit. 'v' to toggle verbose.\n")

    verbose = False

    while True:
        try:
            text = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Closing CCM.")
            break

        if not text:
            continue
        if text.lower() == 'q':
            break
        if text.lower() == 'v':
            verbose = not verbose
            print(f"  Verbose: {'ON' if verbose else 'OFF'}")
            continue

        state = ccm.process_input(text)
        print_state(state, verbose=verbose)

        if viz:
            viz.update(state)


def run_demo():
    """Demo without interactive input — shows the cycle with predefined inputs."""
    ccm = CycleManager()

    inputs = [
        "there is a ghost",
        "the ghost is watching slowly",
        "run",
        "the room is dark and strange",
        "a person",
        "safe light",
    ]

    print("\n  CCM — Demo\n")
    for text in inputs:
        print(f"\n  Input: '{text}'")
        state = ccm.process_input(text)
        print_state(state)

        import time
        time.sleep(0.5)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    elif "--viz" in sys.argv:
        run_interactive(use_viz=True)
    else:
        run_interactive(use_viz=False)
