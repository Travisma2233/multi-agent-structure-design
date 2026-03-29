"""
Two-Story Shear Building — Dynamic Analysis with OpenSeesPy
============================================================
Lumped mass model (2 DOF) with harmonic ground excitation.

Model:
  - m1 = m2 = 20,000 kg
  - k1 = 20 MN/m, k2 = 15 MN/m
  - Rayleigh damping at 5%
  - Newmark integration (gamma=0.5, beta=0.25)

Ground motion:
  - a(t) = 0.3g * sin(2*pi*2*t), duration = 15 s
"""

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ============================================================
# 1. Parameters
# ============================================================
m1, m2 = 20000.0, 20000.0        # Floor masses (kg)
k1, k2 = 20.0e6, 15.0e6          # Story stiffnesses (N/m)
xi = 0.05                         # Damping ratio

g_acc = 9.81                      # Gravity (m/s^2)
amp = 0.3 * g_acc                 # Ground acceleration amplitude
freq = 2.0                        # Excitation frequency (Hz)
dt = 0.01                         # Time step (s)
duration = 15.0                   # Total duration (s)
n_steps = int(duration / dt)

# ============================================================
# 2. OpenSees Model
# ============================================================
ops.wipe()
ops.model('basic', '-ndm', 1, '-ndf', 1)

# Nodes: 0=base, 1=floor1, 2=floor2
ops.node(0, 0.0)
ops.node(1, 0.0)
ops.node(2, 0.0)

# Boundary: fix base
ops.fix(0, 1)

# Masses
ops.mass(1, m1)
ops.mass(2, m2)

# Materials (elastic springs)
ops.uniaxialMaterial('Elastic', 1, k1)
ops.uniaxialMaterial('Elastic', 2, k2)

# ZeroLength spring elements
ops.element('zeroLength', 1, 0, 1, '-mat', 1, '-dir', 1)
ops.element('zeroLength', 2, 1, 2, '-mat', 2, '-dir', 1)

# ============================================================
# 3. Eigen Analysis & Rayleigh Damping
# ============================================================
eigen_values = ops.eigen('-fullGenLapack', 2)
w1 = np.sqrt(eigen_values[0])
w2 = np.sqrt(eigen_values[1])
f1 = w1 / (2.0 * np.pi)
f2 = w2 / (2.0 * np.pi)
T1 = 1.0 / f1
T2 = 1.0 / f2

print("=" * 55)
print("  Modal Analysis Results")
print("=" * 55)
print(f"  Mode 1: ω = {w1:.4f} rad/s,  f = {f1:.4f} Hz,  T = {T1:.4f} s")
print(f"  Mode 2: ω = {w2:.4f} rad/s,  f = {f2:.4f} Hz,  T = {T2:.4f} s")

# Rayleigh coefficients: C = alphaM * M + betaK * K
alphaM = 2.0 * xi * w1 * w2 / (w1 + w2)
betaK = 2.0 * xi / (w1 + w2)
print(f"  Rayleigh: αM = {alphaM:.6f},  βK = {betaK:.6f}")
print("=" * 55)

ops.rayleigh(alphaM, betaK, 0.0, 0.0)

# ============================================================
# 4. Ground Motion (Harmonic)
# ============================================================
period_g = 1.0 / freq
ops.timeSeries('Sine', 1, 0.0, duration, period_g, '-factor', amp)
ops.pattern('UniformExcitation', 1, 1, '-accel', 1)

# ============================================================
# 5. Analysis Configuration (Newmark)
# ============================================================
ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-8, 10)
ops.algorithm('Newton')
ops.integrator('Newmark', 0.5, 0.25)
ops.analysis('Transient')

# ============================================================
# 6. Run Analysis & Record Results
# ============================================================
time_arr = np.zeros(n_steps + 1)
disp1 = np.zeros(n_steps + 1)
disp2 = np.zeros(n_steps + 1)
vel1 = np.zeros(n_steps + 1)
vel2 = np.zeros(n_steps + 1)
accel1 = np.zeros(n_steps + 1)
accel2 = np.zeros(n_steps + 1)

print(f"\nRunning transient analysis: {n_steps} steps × {dt} s ...")

for i in range(1, n_steps + 1):
    ok = ops.analyze(1, dt)
    if ok != 0:
        print(f"  !! Analysis failed at step {i} (t = {i*dt:.3f} s)")
        break

    time_arr[i] = ops.getTime()
    disp1[i] = ops.nodeDisp(1, 1)
    disp2[i] = ops.nodeDisp(2, 1)
    vel1[i] = ops.nodeVel(1, 1)
    vel2[i] = ops.nodeVel(2, 1)
    accel1[i] = ops.nodeAccel(1, 1)
    accel2[i] = ops.nodeAccel(2, 1)

print("Analysis completed successfully!")

# Trim if analysis stopped early
idx = np.argmax(time_arr == 0) if time_arr[-1] == 0 and n_steps > 0 else len(time_arr)
if idx == 0:
    idx = len(time_arr)
time_arr = time_arr[:idx]
disp1 = disp1[:idx]
disp2 = disp2[:idx]

# Story drifts
drift1 = disp1          # story 1 drift (base is fixed → 0)
drift2 = disp2 - disp1  # story 2 drift

# ============================================================
# 7. Summary
# ============================================================
print(f"\n{'=' * 55}")
print("  Response Summary")
print(f"{'=' * 55}")
print(f"  Max Floor 1 displacement:  {np.max(np.abs(disp1))*1000:.3f} mm")
print(f"  Max Floor 2 displacement:  {np.max(np.abs(disp2))*1000:.3f} mm")
print(f"  Max Story 1 drift:         {np.max(np.abs(drift1))*1000:.3f} mm")
print(f"  Max Story 2 drift:         {np.max(np.abs(drift2))*1000:.3f} mm")
print(f"{'=' * 55}")

# ============================================================
# 8. Visualization
# ============================================================
fig = plt.figure(figsize=(16, 10))
fig.suptitle("Two-Story Shear Building — Dynamic Analysis Results",
             fontsize=14, fontweight='bold', y=0.98)

# ── (a) Floor Displacements ───────────────────────────────
ax1 = fig.add_subplot(2, 2, 1)
ax1.plot(time_arr, disp1 * 1000, 'b-', lw=0.7, label='Floor 1')
ax1.plot(time_arr, disp2 * 1000, 'r-', lw=0.7, label='Floor 2')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Displacement (mm)')
ax1.set_title('(a) Floor Displacements')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, duration)

# ── (b) Story Drifts ──────────────────────────────────────
ax2 = fig.add_subplot(2, 2, 2)
ax2.plot(time_arr, drift1 * 1000, 'b-', lw=0.7, label='Story 1')
ax2.plot(time_arr, drift2 * 1000, 'r-', lw=0.7, label='Story 2')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Story Drift (mm)')
ax2.set_title('(b) Story Drifts')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, duration)

# ── (c) Ground Motion ─────────────────────────────────────
ax3 = fig.add_subplot(2, 2, 3)
accel_input = amp * np.sin(2.0 * np.pi * freq * time_arr)
ax3.plot(time_arr, accel_input / g_acc, 'k-', lw=0.5)
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Ground Acceleration (g)')
ax3.set_title('(c) Harmonic Ground Motion (f = 2 Hz, 0.3g)')
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, duration)
ax3.set_ylim(-0.45, 0.45)

# ── (d) Structural Model Schematic ────────────────────────
ax4 = fig.add_subplot(2, 2, 4)
ax4.set_xlim(-3, 3)
ax4.set_ylim(-1.2, 7.5)
ax4.set_aspect('equal')
ax4.set_title('(d) Structural Model')
ax4.axis('off')

# Ground
ax4.plot([-2.5, 2.5], [0, 0], 'k-', lw=2)
for xh in np.arange(-2.3, 2.5, 0.4):
    ax4.plot([xh, xh - 0.3], [0, -0.3], 'k-', lw=0.7)

h1_pos, h2_pos = 3.0, 6.0
slab_w = 2.0


def draw_spring(ax, x, y_bot, y_top, n_coils=6, width=0.4):
    """Draw a zigzag spring between y_bot and y_top at x."""
    margin = 0.3
    coil_pts = n_coils * 2 + 1
    ys_coil = np.linspace(y_bot + margin, y_top - margin, coil_pts)
    xs_coil = np.zeros(coil_pts)
    xs_coil[0] = x
    xs_coil[-1] = x
    for i in range(1, coil_pts - 1):
        xs_coil[i] = x + width if i % 2 == 1 else x - width
    # Add straight leads at top and bottom
    all_x = [x] + list(xs_coil) + [x]
    all_y = [y_bot] + list(ys_coil) + [y_top]
    ax.plot(all_x, all_y, 'b-', lw=1.2)


# Springs
draw_spring(ax4, -1.0, 0, h1_pos)
draw_spring(ax4, 1.0, 0, h1_pos)
draw_spring(ax4, -1.0, h1_pos, h2_pos)
draw_spring(ax4, 1.0, h1_pos, h2_pos)

# Floor slabs
for h in [h1_pos, h2_pos]:
    ax4.plot([-slab_w, slab_w], [h, h], 'k-', lw=3)

# Mass nodes
ax4.plot(0, h1_pos, 'ko', ms=12, zorder=5)
ax4.plot(0, h2_pos, 'ko', ms=12, zorder=5)

# Labels
ax4.annotate('m₁ = 20 t', (0, h1_pos), (2.2, h1_pos),
             fontsize=9, ha='left', va='center',
             arrowprops=dict(arrowstyle='->', color='gray'))
ax4.annotate('m₂ = 20 t', (0, h2_pos), (2.2, h2_pos),
             fontsize=9, ha='left', va='center',
             arrowprops=dict(arrowstyle='->', color='gray'))

ax4.text(-2.4, h1_pos / 2, 'k₁ = 20\nMN/m', fontsize=8, ha='center', va='center',
         bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='gray'))
ax4.text(-2.4, (h1_pos + h2_pos) / 2, 'k₂ = 15\nMN/m', fontsize=8, ha='center', va='center',
         bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='gray'))

# Ground motion arrow
ax4.annotate('', xy=(1.8, -0.7), xytext=(0.3, -0.7),
             arrowprops=dict(arrowstyle='<->', color='red', lw=2))
ax4.text(1.05, -1.05, 'a(t) = 0.3g·sin(2π·2·t)', fontsize=8,
         ha='center', color='red', fontweight='bold')

# Node labels
ax4.text(0, -0.45, 'Base (fixed)', fontsize=8, ha='center', color='gray')
ax4.text(-0.3, h1_pos + 0.35, 'Node 1', fontsize=8, ha='center', color='blue')
ax4.text(-0.3, h2_pos + 0.35, 'Node 2', fontsize=8, ha='center', color='blue')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('results.png', dpi=150, bbox_inches='tight')
print("\nPlot saved to results.png")
plt.show()

ops.wipe()
