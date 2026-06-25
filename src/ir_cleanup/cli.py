#!/usr/bin/env python3

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf


def main():
    parser = argparse.ArgumentParser(
        description="Truncate an impulse response file based on energy content.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", help="Input IR file (WAV, FLAC, AIFF, OGG, ...)")
    parser.add_argument("output", help="Output IR file")
    parser.add_argument(
        "energy_percent",
        type=float,
        help="Percentage of total energy to retain (0 < value < 100)",
    )
    parser.add_argument(
        "--fade-length",
        type=float,
        default=None,
        metavar="MS",
        help="Fade-out duration in milliseconds (default: 256 samples)",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip the plot display",
    )
    parser.add_argument(
        "--save-plot",
        metavar="FILE",
        help="Save the plot to FILE instead of (or in addition to) displaying it",
    )

    args = parser.parse_args()

    if not (0 < args.energy_percent < 100):
        parser.error("energy_percent must be strictly between 0 and 100")

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    try:
        ir, samplerate = sf.read(args.input, always_2d=True)
    except Exception as e:
        parser.error(f"Could not read input file: {e}")

    n_channels = ir.shape[1]

    # Mono mix for analysis only
    ir_mono = ir.mean(axis=1)

    # ------------------------------------------------------------------
    # Peak detection
    # ------------------------------------------------------------------

    peak_index = int(np.argmax(np.abs(ir_mono)))
    print(f"Peak detected at sample {peak_index}")

    ir = ir[peak_index:]
    ir_mono = ir_mono[peak_index:]

    # ------------------------------------------------------------------
    # Cumulative energy
    # ------------------------------------------------------------------

    energy = ir_mono ** 2
    total_energy = energy.sum()

    if total_energy == 0:
        sys.exit("Error: IR contains no energy")

    cumulative_energy = np.cumsum(energy) / total_energy
    threshold = args.energy_percent / 100.0
    cut_index = int(np.searchsorted(cumulative_energy, threshold))

    ir_truncated = ir[:cut_index + 1]

    # ------------------------------------------------------------------
    # Fade-out
    # ------------------------------------------------------------------

    if args.fade_length is not None:
        fade_samples = int(round(args.fade_length * samplerate / 1000.0))
    else:
        fade_samples = 256

    fade_length = min(fade_samples, len(ir_truncated))

    if fade_length > 1:
        fade = np.linspace(1.0, 0.0, fade_length)
        ir_truncated[-fade_length:] *= fade[:, np.newaxis]

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    try:
        sf.write(args.output, ir_truncated if n_channels > 1 else ir_truncated[:, 0], samplerate)
    except Exception as e:
        sys.exit(f"Error: Could not write output file: {e}")

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    original_duration_ms = len(ir) * 1000.0 / samplerate
    new_duration_ms = len(ir_truncated) * 1000.0 / samplerate
    retained_energy = cumulative_energy[cut_index] * 100.0

    print()
    print(f"Channels        : {n_channels}")
    print(f"Sample rate     : {samplerate} Hz")
    print(f"Original length : {len(ir)} samples ({original_duration_ms:.2f} ms)")
    print(f"New length      : {len(ir_truncated)} samples ({new_duration_ms:.2f} ms)")
    print(f"Retained energy : {retained_energy:.5f}%")
    print(f"Fade-out length : {fade_length} samples ({fade_length * 1000.0 / samplerate:.2f} ms)")

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------

    if not args.no_plot or args.save_plot:
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        axes[0].plot(ir_mono)
        axes[0].axvline(cut_index, linestyle="--", label=f"Cut ({args.energy_percent:.3f}%)")
        axes[0].set_title("Impulse Response (mono mix)")
        axes[0].set_xlabel("Sample")
        axes[0].set_ylabel("Amplitude")
        axes[0].grid(True)
        axes[0].legend()

        axes[1].plot(cumulative_energy * 100.0)
        axes[1].axhline(args.energy_percent, linestyle="--", label=f"{args.energy_percent:.3f}%")
        axes[1].axvline(cut_index, linestyle="--")
        axes[1].set_title("Cumulative Energy")
        axes[1].set_xlabel("Sample")
        axes[1].set_ylabel("Energy (%)")
        axes[1].grid(True)
        axes[1].legend()

        plt.tight_layout()

        if args.save_plot:
            fig.savefig(args.save_plot, dpi=150)
            print(f"Plot saved to {args.save_plot}")

        if not args.no_plot:
            plt.show()
