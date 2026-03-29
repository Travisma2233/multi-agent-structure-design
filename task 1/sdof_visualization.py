"""
SDOF Model Visualization
=========================
Draws the physical schematic: fixed support, spring, free node, and force arrow.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def draw_spring(ax, x_start, x_end, y, n_coils=6, amplitude=0.15):
    """Draw a zig-zag spring between two x positions."""
    length = x_end - x_start
    # Straight leads at each end
    lead = length * 0.1
    coil_length = length - 2 * lead
    x_points = [x_start, x_start + lead]
    y_points = [y, y]

    for i in range(n_coils * 2):
        x_points.append(x_start + lead + coil_length * (i + 0.5) / (n_coils * 2))
        y_points.append(y + amplitude * (1 if i % 2 == 0 else -1))

    x_points += [x_end - lead, x_end]
    y_points += [y, y]

    ax.plot(x_points, y_points, 'k-', linewidth=1.8)


def draw_fixed_support(ax, x, y, size=0.3):
    """Draw a hatched fixed support (ground symbol)."""
    # Vertical wall
    ax.plot([x, x], [y - size, y + size], 'k-', linewidth=2.5)
    # Hatch lines
    for yi in np.linspace(y - size, y + size, 6):
        ax.plot([x - 0.12, x], [yi - 0.08, yi], 'k-', linewidth=1)


fig, ax = plt.subplots(figsize=(10, 4))

# Positions
x_fixed = 1.0
x_free = 4.0
y = 2.0

# Fixed support
draw_fixed_support(ax, x_fixed, y)

# Node 1 (fixed)
ax.plot(x_fixed, y, 'ko', markersize=10, zorder=5)
ax.text(x_fixed, y - 0.45, 'Node 1\n(fixed)', ha='center', fontsize=10,
        fontweight='bold', color='#444')

# Spring element
draw_spring(ax, x_fixed, x_free, y)
ax.text((x_fixed + x_free) / 2, y + 0.35, 'k = 20000 N/m',
        ha='center', fontsize=10, color='#2563eb', fontweight='bold')

# Node 2 (free)
ax.plot(x_free, y, 'o', color='#2563eb', markersize=12, zorder=5,
        markeredgecolor='black', markeredgewidth=1.5)
ax.text(x_free, y - 0.45, 'Node 2\n(free)', ha='center', fontsize=10,
        fontweight='bold', color='#2563eb')

# Force arrow
arrow_start = x_free + 0.15
arrow_len = 1.2
ax.annotate('', xy=(x_free + 0.05, y), xytext=(x_free + arrow_len, y),
            arrowprops=dict(arrowstyle='->', color='#dc2626', lw=2.5))
ax.text(x_free + arrow_len / 2 + 0.3, y + 0.2, 'F = 10 kN',
        fontsize=12, fontweight='bold', color='#dc2626', ha='center')

# Displacement indicator
ax.annotate('', xy=(x_free + 0.6, y - 0.7), xytext=(x_free, y - 0.7),
            arrowprops=dict(arrowstyle='->', color='#16a34a', lw=1.5))
ax.text(x_free + 0.3, y - 0.9, 'u₂', fontsize=11, ha='center',
        color='#16a34a', fontstyle='italic')

# Title
ax.set_title('SDOF System — zeroLength Spring Model', fontsize=14, fontweight='bold')

ax.set_xlim(0.3, 6.0)
ax.set_ylim(0.8, 3.0)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
plt.savefig('sdof_model.png', dpi=150, bbox_inches='tight')
print("Saved: sdof_model.png")
plt.show()
