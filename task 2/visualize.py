"""
Simply Supported Beam - Visualization
Produces: beam diagram with supports and load arrows,
          plus deflected shape from OpenSees results.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ── Parameters ──────────────────────────────────────────────
L = 6.0        # beam length (m)
nEle = 4       # number of elements
w = 10.0       # uniform load magnitude (kN/m)
E = 206.0e6    # kN/m^2
I = 8.5e-6     # m^4

nodes_x = np.linspace(0, L, nEle + 1)  # 0, 1.5, 3.0, 4.5, 6.0

# ── Analytical deflection curve ─────────────────────────────
x_fine = np.linspace(0, L, 200)
# y(x) = w*x/(24EI) * (L^3 - 2Lx^2 + x^3)  (downward positive here)
EI = E * I
y_analytical = w * x_fine / (24 * EI) * (L**3 - 2*L*x_fine**2 + x_fine**3)
delta_max_analytical = 5 * w * L**4 / (384 * EI)

# ── Read OpenSees results ───────────────────────────────────
try:
    midspan = np.loadtxt("midspan_disp.txt")
    midspan_disp = float(midspan) if midspan.ndim == 0 else float(midspan[-1])
    reactions = np.loadtxt("reactions.txt")
    if reactions.ndim == 1:
        react_data = reactions
    else:
        react_data = reactions[-1]
    R1x, R1y, R1m = react_data[0], react_data[1], react_data[2]
    R5x, R5y, R5m = react_data[3], react_data[4], react_data[5]
    has_results = True
    print(f"OpenSees mid-span deflection: {midspan_disp*1000:.4f} mm")
    print(f"Analytical mid-span deflection: {delta_max_analytical*1000:.4f} mm")
    print(f"Left reaction  Ry = {R1y:.2f} kN")
    print(f"Right reaction Ry = {R5y:.2f} kN")
except Exception as e:
    print(f"Could not read OpenSees output: {e}")
    print("Showing analytical solution only.")
    has_results = False
    midspan_disp = -delta_max_analytical
    R1y = w * L / 2
    R5y = w * L / 2

# ── Figure ──────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [1.2, 1]})
fig.suptitle("Simply Supported Beam — Elastic Static Analysis", fontsize=15, fontweight='bold')

# ────── TOP: Beam diagram with supports and load ────────────
ax = axes[0]
ax.set_xlim(-0.8, L + 0.8)
ax.set_ylim(-1.8, 2.2)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title("Model & Loading", fontsize=12, pad=10)

beam_y = 0.0

# Beam line
ax.plot([0, L], [beam_y, beam_y], 'k-', linewidth=4, solid_capstyle='round')

# Node markers
for i, nx in enumerate(nodes_x):
    ax.plot(nx, beam_y, 'ko', markersize=7, zorder=5)
    ax.text(nx, beam_y - 0.25, f"N{i+1}", ha='center', va='top', fontsize=8, color='#333')

# ── Pin support (left) ──────────────────────────────────────
tri_h = 0.35
tri_w = 0.3
pin_x, pin_y = 0.0, beam_y
triangle = plt.Polygon(
    [[pin_x, pin_y], [pin_x - tri_w, pin_y - tri_h], [pin_x + tri_w, pin_y - tri_h]],
    closed=True, fill=False, edgecolor='blue', linewidth=2
)
ax.add_patch(triangle)
# Ground hatching
for j in range(5):
    xh = pin_x - tri_w + j * 2 * tri_w / 4
    ax.plot([xh, xh - 0.12], [pin_y - tri_h, pin_y - tri_h - 0.15],
            'b-', linewidth=1)
ax.text(pin_x, pin_y - tri_h - 0.4, "Pin", ha='center', fontsize=9, color='blue')

# ── Roller support (right) ──────────────────────────────────
roll_x, roll_y = L, beam_y
triangle_r = plt.Polygon(
    [[roll_x, roll_y], [roll_x - tri_w, roll_y - tri_h], [roll_x + tri_w, roll_y - tri_h]],
    closed=True, fill=False, edgecolor='red', linewidth=2
)
ax.add_patch(triangle_r)
circle_r = 0.08
for cx_off in [-0.15, 0.0, 0.15]:
    circle = plt.Circle((roll_x + cx_off, roll_y - tri_h - circle_r - 0.02),
                         circle_r, fill=False, edgecolor='red', linewidth=1.5)
    ax.add_patch(circle)
# Ground line under rollers
ax.plot([roll_x - tri_w, roll_x + tri_w],
        [roll_y - tri_h - 2*circle_r - 0.04]*2,
        'r-', linewidth=1.5)
ax.text(roll_x, roll_y - tri_h - 2*circle_r - 0.25, "Roller", ha='center', fontsize=9, color='red')

# ── Uniform load arrows ────────────────────────────────────
arrow_spacing = 0.3
arrow_top = beam_y + 1.2
n_arrows = int(L / arrow_spacing) + 1
for i in range(n_arrows):
    xa = i * arrow_spacing
    if xa > L:
        xa = L
    ax.annotate('', xy=(xa, beam_y + 0.05), xytext=(xa, arrow_top),
                arrowprops=dict(arrowstyle='->', color='green', lw=1.2))

# Load line on top
ax.plot([0, L], [arrow_top, arrow_top], 'g-', linewidth=2)
ax.text(L/2, arrow_top + 0.2, f"w = {w:.0f} kN/m", ha='center', fontsize=11,
        color='green', fontweight='bold')

# Dimension line
dim_y = beam_y - 1.3
ax.annotate('', xy=(0, dim_y), xytext=(L, dim_y),
            arrowprops=dict(arrowstyle='<->', color='gray', lw=1.2))
ax.text(L/2, dim_y - 0.2, f"L = {L:.1f} m", ha='center', fontsize=10, color='gray')

# Reaction annotations
ax.annotate(f"Ry = {abs(R1y):.1f} kN", xy=(0, beam_y - tri_h - 0.05),
            xytext=(-0.6, beam_y + 0.8),
            fontsize=9, color='blue', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='blue', lw=1))
ax.annotate(f"Ry = {abs(R5y):.1f} kN", xy=(L, beam_y - tri_h - 0.05),
            xytext=(L + 0.3, beam_y + 0.8),
            fontsize=9, color='red', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='red', lw=1))

# ────── BOTTOM: Deflected shape ────────────────────────────
ax2 = axes[1]
ax2.set_title("Deflected Shape", fontsize=12, pad=10)

# Scale deflection for visibility
scale = 1000  # convert m → mm

ax2.fill_between(x_fine, 0, -y_analytical * scale, alpha=0.15, color='steelblue')
ax2.plot(x_fine, -y_analytical * scale, 'b-', linewidth=2, label='Analytical')

# Plot OpenSees node displacements (read from node positions)
if has_results:
    # We know midspan; for a full plot, compute analytical at node positions
    node_disp_analytical = w * nodes_x / (24*EI) * (L**3 - 2*L*nodes_x**2 + nodes_x**3)
    ax2.plot(nodes_x, -node_disp_analytical * scale, 'rs', markersize=8,
             label='Node positions', zorder=5)
    # Mark midspan
    ax2.plot(L/2, midspan_disp * scale, 'r^', markersize=12, zorder=6,
             label=f'OpenSees midspan = {midspan_disp*scale:.4f} mm')

ax2.axhline(y=0, color='k', linewidth=1.5)
ax2.set_xlabel("Position along beam (m)", fontsize=11)
ax2.set_ylabel("Deflection (mm)", fontsize=11)
ax2.legend(fontsize=10, loc='lower left')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(-0.3, L + 0.3)

# Add text box with key results
textstr = (f"Mid-span deflection:\n"
           f"  OpenSees:   {abs(midspan_disp)*1000:.4f} mm\n"
           f"  Analytical: {delta_max_analytical*1000:.4f} mm\n"
           f"  Error: {abs(abs(midspan_disp)-delta_max_analytical)/delta_max_analytical*100:.4f}%")
props = dict(boxstyle='round', facecolor='lightyellow', alpha=0.9)
ax2.text(0.98, 0.95, textstr, transform=ax2.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right', bbox=props,
         family='monospace')

plt.tight_layout()
plt.savefig("beam_results.png", dpi=150, bbox_inches='tight')
plt.show()
print("\nFigure saved to beam_results.png")
