"""
Simply Supported Beam - Elastic Static Analysis (OpenSeesPy)
Units: kN, m
"""

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ============================================================
# 1. OpenSees Analysis
# ============================================================
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Parameters
L    = 6.0        # beam length (m)
nEle = 4          # number of elements
dL   = L / nEle   # element length = 1.5 m
E    = 206.0e6    # Young's modulus (kN/m^2)
A    = 0.01       # cross-section area (m^2)
Iz   = 8.5e-6     # moment of inertia (m^4)
w    = 10.0       # uniform load magnitude (kN/m)

# Nodes: 1 through 5 at x = 0, 1.5, 3.0, 4.5, 6.0
for i in range(1, nEle + 2):
    ops.node(i, (i - 1) * dL, 0.0)

# Boundary conditions
ops.fix(1,         1, 1, 0)   # Pin:    fix x, y
ops.fix(nEle + 1,  0, 1, 0)   # Roller: fix y only

# Geometric transformation
ops.geomTransf('Linear', 1)

# Elements: elasticBeamColumn
for i in range(1, nEle + 1):
    ops.element('elasticBeamColumn', i, i, i + 1, A, E, Iz, 1)

# Load pattern: uniform distributed load (negative = downward)
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
for i in range(1, nEle + 1):
    ops.eleLoad('-ele', i, '-type', '-beamUniform', -w)

# Analysis
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

# ============================================================
# 2. Extract Results
# ============================================================
ops.reactions()

# Node displacements
node_x   = []
node_dy  = []
node_rot = []
for i in range(1, nEle + 2):
    node_x.append((i - 1) * dL)
    node_dy.append(ops.nodeDisp(i, 2))
    node_rot.append(ops.nodeDisp(i, 3))

# Reactions
R1 = [ops.nodeReaction(1, d) for d in [1, 2, 3]]
R5 = [ops.nodeReaction(nEle + 1, d) for d in [1, 2, 3]]

# Mid-span deflection (node 3)
mid_node  = nEle // 2 + 1  # node 3
mid_disp  = ops.nodeDisp(mid_node, 2)

ops.wipe()

# ============================================================
# 3. Analytical Solution
# ============================================================
EI = E * Iz
delta_analytical = 5 * w * L**4 / (384 * EI)
R_analytical     = w * L / 2

x_fine = np.linspace(0, L, 300)
y_analytical = w * x_fine / (24 * EI) * (L**3 - 2*L*x_fine**2 + x_fine**3)

# ============================================================
# 4. Print Results
# ============================================================
print("=" * 55)
print(" Simply Supported Beam - Elastic Static Analysis")
print("=" * 55)
print(f"\n  Beam length:   {L} m")
print(f"  Elements:      {nEle}")
print(f"  E = {E:.3e} kN/m^2   A = {A} m^2   I = {Iz:.2e} m^4")
print(f"  Uniform load:  {w} kN/m (downward)")

print("\n-- Support Reactions ----------------------------------")
print(f"  Left  pin    (Node 1): Rx={R1[0]:+.4f} kN  Ry={R1[1]:+.4f} kN  M={R1[2]:+.4f} kN*m")
print(f"  Right roller (Node 5): Rx={R5[0]:+.4f} kN  Ry={R5[1]:+.4f} kN  M={R5[2]:+.4f} kN*m")
print(f"  Analytical Ry = +/-{R_analytical:.4f} kN")

print("\n-- Node Displacements ---------------------------------")
print(f"  {'Node':<6} {'x (m)':<10} {'dy (m)':<18} {'rot (rad)':<18}")
for i in range(nEle + 1):
    print(f"  {i+1:<6} {node_x[i]:<10.3f} {node_dy[i]:<18.6e} {node_rot[i]:<18.6e}")

print("\n-- Mid-span Deflection --------------------------------")
print(f"  OpenSees:   {abs(mid_disp)*1000:.4f} mm  ({mid_disp:.6e} m)")
print(f"  Analytical: {delta_analytical*1000:.4f} mm  ({delta_analytical:.6e} m)")
error = abs(abs(mid_disp) - delta_analytical) / delta_analytical * 100
print(f"  Error:      {error:.4f} %")
print("=" * 55)

# ============================================================
# 5. Visualization
# ============================================================
fig, axes = plt.subplots(2, 1, figsize=(13, 8.5),
                         gridspec_kw={'height_ratios': [1.2, 1]})
fig.suptitle("Simply Supported Beam — Elastic Static Analysis",
             fontsize=15, fontweight='bold', y=0.98)

# ── Top panel: beam diagram ─────────────────────────────────
ax = axes[0]
ax.set_xlim(-1.0, L + 1.0)
ax.set_ylim(-2.0, 2.5)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title("Model & Loading", fontsize=12, pad=8)

by = 0.0  # beam y-coordinate

# Beam
ax.plot([0, L], [by, by], 'k-', lw=4, solid_capstyle='round')

# Nodes
nodes_xarr = np.array(node_x)
for i, nx in enumerate(nodes_xarr):
    ax.plot(nx, by, 'ko', ms=7, zorder=5)
    ax.text(nx, by - 0.28, f"N{i+1}", ha='center', va='top', fontsize=8, color='#444')

# --- Pin support (left) ---
th, tw = 0.35, 0.3
tri = plt.Polygon([[0, by], [-tw, by - th], [tw, by - th]],
                   closed=True, fill=False, ec='blue', lw=2)
ax.add_patch(tri)
for j in range(6):
    xh = -tw + j * 2*tw/5
    ax.plot([xh, xh - 0.12], [by - th, by - th - 0.15], 'b-', lw=1)
ax.text(0, by - th - 0.45, "Pin", ha='center', fontsize=9, color='blue', fontweight='bold')

# --- Roller support (right) ---
tri_r = plt.Polygon([[L, by], [L - tw, by - th], [L + tw, by - th]],
                     closed=True, fill=False, ec='red', lw=2)
ax.add_patch(tri_r)
cr = 0.08
for off in [-0.15, 0.0, 0.15]:
    circ = plt.Circle((L + off, by - th - cr - 0.02), cr, fill=False, ec='red', lw=1.5)
    ax.add_patch(circ)
ax.plot([L - tw, L + tw], [by - th - 2*cr - 0.04]*2, 'r-', lw=1.5)
ax.text(L, by - th - 2*cr - 0.35, "Roller", ha='center', fontsize=9, color='red', fontweight='bold')

# --- Uniform load arrows ---
arrow_top = by + 1.3
n_arrows = int(L / 0.3) + 1
for k in range(n_arrows):
    xa = min(k * 0.3, L)
    ax.annotate('', xy=(xa, by + 0.08), xytext=(xa, arrow_top),
                arrowprops=dict(arrowstyle='->', color='green', lw=1.2))
ax.plot([0, L], [arrow_top, arrow_top], 'g-', lw=2)
ax.text(L/2, arrow_top + 0.25, f"w = {w:.0f} kN/m",
        ha='center', fontsize=11, color='green', fontweight='bold')

# Dimension line
dy_dim = by - 1.4
ax.annotate('', xy=(0, dy_dim), xytext=(L, dy_dim),
            arrowprops=dict(arrowstyle='<->', color='gray', lw=1.2))
ax.text(L/2, dy_dim - 0.25, f"L = {L:.1f} m", ha='center', fontsize=10, color='gray')

# Reaction labels
ax.annotate(f"Ry = {abs(R1[1]):.1f} kN", xy=(0, by - th),
            xytext=(-0.7, by + 0.9), fontsize=9, color='blue', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='blue', lw=1))
ax.annotate(f"Ry = {abs(R5[1]):.1f} kN", xy=(L, by - th),
            xytext=(L + 0.3, by + 0.9), fontsize=9, color='red', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='red', lw=1))

# ── Bottom panel: deflected shape ───────────────────────────
ax2 = axes[1]
ax2.set_title("Deflected Shape", fontsize=12, pad=8)

# Analytical (downward shown as negative)
ax2.fill_between(x_fine, 0, -y_analytical * 1000, alpha=0.15, color='steelblue')
ax2.plot(x_fine, -y_analytical * 1000, 'b-', lw=2.2, label='Analytical')

# OpenSees node results
node_dy_mm = np.array(node_dy) * 1000
ax2.plot(nodes_xarr, node_dy_mm, 'rs', ms=9, zorder=5, label='OpenSees nodes')

# Highlight midspan
ax2.plot(nodes_xarr[mid_node - 1], node_dy_mm[mid_node - 1], 'r^', ms=14, zorder=6,
         label=f'Midspan = {mid_disp*1000:.4f} mm')

ax2.axhline(0, color='k', lw=1.5)
ax2.set_xlabel("Position along beam (m)", fontsize=11)
ax2.set_ylabel("Deflection (mm)", fontsize=11)
ax2.legend(fontsize=10, loc='lower left')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(-0.3, L + 0.3)

# Result box
txt = (f"Mid-span deflection:\n"
       f"  OpenSees:   {abs(mid_disp)*1000:.4f} mm\n"
       f"  Analytical: {delta_analytical*1000:.4f} mm\n"
       f"  Error: {error:.4f} %\n"
       f"\nReactions:\n"
       f"  Left  Ry = {abs(R1[1]):.2f} kN\n"
       f"  Right Ry = {abs(R5[1]):.2f} kN")
ax2.text(0.98, 0.98, txt, transform=ax2.transAxes, fontsize=9,
         va='top', ha='right', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

plt.tight_layout()
plt.savefig("beam_results.png", dpi=150, bbox_inches='tight')
print("\nFigure saved: beam_results.png")
plt.show()
