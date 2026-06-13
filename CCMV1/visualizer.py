# visualizer.py
# Matplotlib visualization of the two CCM engines
# Shows: external engine (blue), internal engine (orange), current state (white)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.animation import FuncAnimation


def draw_motor(ax, ext_x, ext_y, int_x, int_y, title, labels, max_red=True):
    ax.clear()
    ax.set_facecolor('#1a1a1a')
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect('equal')
    ax.set_title(title, color='#cccccc', fontsize=11, pad=8)
    ax.tick_params(colors='#555555')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')

    # Heat rings
    n_rings = 7
    colors_red    = ['#1a5c1a','#3a7a1a','#7a7a10','#aa5010','#cc3010','#dd1818','#ee0000']
    colors_orange = ['#1a5c1a','#3a7a1a','#7a7a10','#aa5010','#cc5010','#dd6010','#ee7010']
    ring_colors = colors_red if max_red else colors_orange

    for i in range(n_rings, 0, -1):
        r     = i / n_rings
        alpha = 0.12 + (i / n_rings) * 0.45
        circle = plt.Circle((0, 0), r, color=ring_colors[i-1], alpha=alpha, zorder=1)
        ax.add_patch(circle)

    # Outer border
    outer = plt.Circle((0, 0), 1.0, fill=False, color='#444444', linewidth=0.8, zorder=2)
    ax.add_patch(outer)

    # Axes
    ax.axhline(0, color='#333333', linewidth=0.5, linestyle='--', zorder=3)
    ax.axvline(0, color='#333333', linewidth=0.5, linestyle='--', zorder=3)

    # Axis labels
    ax.text(0,     1.25,  labels['top'],    ha='center', va='center', color='#888888', fontsize=8)
    ax.text(0,    -1.25,  labels['bottom'], ha='center', va='center', color='#888888', fontsize=8)
    ax.text(-1.25, 0,     labels['left'],   ha='center', va='center', color='#888888', fontsize=8, rotation=90)
    ax.text(1.25,  0,     labels['right'],  ha='center', va='center', color='#888888', fontsize=8, rotation=90)

    # Lines from motors to center
    ax.plot([0, ext_x], [0, ext_y], color='#6ab4ff', linewidth=0.8, alpha=0.4, zorder=4)
    ax.plot([0, int_x], [0, int_y], color='#ffa050', linewidth=0.8, alpha=0.4, zorder=4)

    # Current state (median point)
    cur_x = (ext_x + int_x) / 2
    cur_y = (ext_y + int_y) / 2

    # Dotted line between ext and int
    ax.plot([ext_x, int_x], [ext_y, int_y], color='#555555', linewidth=0.6,
            linestyle=':', zorder=4)

    # External engine (blue)
    ax.plot(ext_x, ext_y, 'o', color='#6ab4ff', markersize=10, zorder=6)
    ax.plot(ext_x, ext_y, 'o', color='white',   markersize=5,  zorder=7)

    # Internal engine (orange)
    ax.plot(int_x, int_y, 'o', color='#ffa050', markersize=10, zorder=6)
    ax.plot(int_x, int_y, 'o', color='white',   markersize=5,  zorder=7)

    # Current state (white with black center)
    ax.plot(cur_x, cur_y, 'o', color='white',   markersize=13, zorder=8)
    ax.plot(cur_x, cur_y, 'o', color='#111111', markersize=6,  zorder=9)

    # Distance to center
    dist = np.sqrt(cur_x**2 + cur_y**2)
    ax.text(0, -1.38, f"dist: {dist:.2f}", ha='center', color='#666666', fontsize=7)

    ax.set_xticks([])
    ax.set_yticks([])


class CCMVisualizer:
    def __init__(self, cycle_manager):
        self.ccm = cycle_manager
        self.fig, self.axes = plt.subplots(1, 2, figsize=(11, 6))
        self.fig.patch.set_facecolor('#111111')
        self.fig.suptitle('CCM — Current State', color='#aaaaaa', fontsize=13)

        self.somatic_labels = {
            'top': 'viable', 'bottom': 'inviable',
            'left': 'global', 'right': 'local'
        }
        self.mental_labels = {
            'top': 'present', 'bottom': 'absent',
            'left': 'rational', 'right': 'emotional'
        }

        # Legend
        self.fig.text(0.5, 0.02,
            '● external (blue)   ● internal (orange)   ● current state (white)',
            ha='center', color='#666666', fontsize=8)

        plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    def update(self, state):
        s = state["somatic"]
        m = state["mental"]

        s_ext_x = s["external"]["Lv"] - s["external"]["Gv"]
        s_ext_y = s["external"]["V"]  - s["external"]["I"]
        s_int_x = s["internal"]["Lv"] - s["internal"]["Gv"]
        s_int_y = s["internal"]["V"]  - s["internal"]["I"]

        m_ext_x = m["external"]["Er"] - m["external"]["Rr"]
        m_ext_y = m["external"]["P"]  - m["external"]["A"]
        m_int_x = m["internal"]["Er"] - m["internal"]["Rr"]
        m_int_y = m["internal"]["P"]  - m["internal"]["A"]

        draw_motor(self.axes[0], s_ext_x, s_ext_y, s_int_x, s_int_y,
                   f'Somatic Engine  D={s["D"]:+.3f}  [{s["tension"]}]',
                   self.somatic_labels, max_red=True)

        draw_motor(self.axes[1], m_ext_x, m_ext_y, m_int_x, m_int_y,
                   f'Mental Engine   C={m["C"]:+.3f}  [{m["tension"]}]',
                   self.mental_labels, max_red=False)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def show(self):
        plt.ion()
        plt.show()
