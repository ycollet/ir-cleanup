#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import sys

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} input.wav output.wav energy_percent")
    print(f"Example: {sys.argv[0]} ir.wav ir_99_9.wav 99.9")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]
energy_percent = float(sys.argv[3])

if not (0 < energy_percent < 100):
    raise ValueError("energy_percent must be between 0 and 100")

# ------------------------------------------------------------------
# Lecture
# ------------------------------------------------------------------

ir, samplerate = sf.read(input_file)

# Conversion mono si besoin
if ir.ndim > 1:
    ir = np.mean(ir, axis=1)

# ------------------------------------------------------------------
# Détection du pic principal
# ------------------------------------------------------------------

peak_index = np.argmax(np.abs(ir))

print(f"Peak detected at sample {peak_index}")

# Recentrage de l'IR sur le pic principal
ir = ir[peak_index:]

# ------------------------------------------------------------------
# Calcul énergie cumulée
# ------------------------------------------------------------------

energy = ir ** 2

total_energy = np.sum(energy)

if total_energy == 0:
    raise RuntimeError("IR contains no energy")

cumulative_energy = np.cumsum(energy)
cumulative_energy /= total_energy

threshold = energy_percent / 100.0

cut_index = np.searchsorted(
    cumulative_energy,
    threshold
)

ir_truncated = ir[:cut_index + 1]

# ------------------------------------------------------------------
# Fade-out
# ------------------------------------------------------------------

fade_length = min(256, len(ir_truncated))

if fade_length > 1:
    fade = np.linspace(
        1.0,
        0.0,
        fade_length
    )

    ir_truncated[-fade_length:] *= fade

# ------------------------------------------------------------------
# Sauvegarde
# ------------------------------------------------------------------

sf.write(
    output_file,
    ir_truncated,
    samplerate
)

# ------------------------------------------------------------------
# Statistiques
# ------------------------------------------------------------------

original_duration_ms = (
    len(ir) * 1000.0 / samplerate
)

new_duration_ms = (
    len(ir_truncated) * 1000.0 / samplerate
)

retained_energy = (
    cumulative_energy[cut_index] * 100.0
)

print()
print(f"Original length : {len(ir)} samples ({original_duration_ms:.2f} ms)")
print(f"New length      : {len(ir_truncated)} samples ({new_duration_ms:.2f} ms)")
print(f"Retained energy : {retained_energy:.5f}%")
print(f"Fade-out length : {fade_length} samples")

# ------------------------------------------------------------------
# Graphiques
# ------------------------------------------------------------------

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# ----- IR -----

axes[0].plot(ir)
axes[0].axvline(
    cut_index,
    linestyle="--",
    label=f"Cut ({energy_percent:.3f}%)"
)

axes[0].set_title("Impulse Response")
axes[0].set_xlabel("Sample")
axes[0].set_ylabel("Amplitude")
axes[0].grid(True)
axes[0].legend()

# ----- Énergie cumulée -----

axes[1].plot(cumulative_energy * 100.0)

axes[1].axhline(
    energy_percent,
    linestyle="--",
    label=f"{energy_percent:.3f}%"
)

axes[1].axvline(
    cut_index,
    linestyle="--"
)

axes[1].set_title("Cumulative Energy")
axes[1].set_xlabel("Sample")
axes[1].set_ylabel("Energy (%)")
axes[1].grid(True)
axes[1].legend()

plt.tight_layout()
plt.show()
