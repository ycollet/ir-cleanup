# ir-cleanup

A command-line tool to truncate impulse response (IR) audio files based on energy content.

## What it does

Given an IR file, the tool:

1. Detects the peak sample and trims any leading content before it
2. Finds the point where the signal has accumulated a given percentage of its total energy
3. Cuts the IR at that point
4. Applies a short linear fade-out (up to 256 samples) at the end to avoid a hard cutoff
5. Plots the waveform and cumulative energy curve with the cut point highlighted

This reduces reverb tail length while retaining a configurable amount of the original energy.

## Installation

```bash
pip install .
```

## Usage

```bash
ir_cleanup <input.wav> <output.wav> <energy_percent>
```

| Argument | Description |
|---|---|
| `input.wav` | Input IR file (WAV) |
| `output.wav` | Output truncated IR file (WAV) |
| `energy_percent` | Energy to retain, strictly between 0 and 100 (e.g. `99.9`) |

### Example

```bash
ir_cleanup room.wav room_truncated.wav 99.9
```

This keeps 99.9% of the total energy and writes the shortened IR to `room_truncated.wav`.

## Notes

- Multi-channel files are downmixed to mono for energy analysis; the output is mono.
- The sample rate is preserved from the input file.

## Dependencies

- [numpy](https://numpy.org/)
- [soundfile](https://python-soundfile.readthedocs.io/)
- [matplotlib](https://matplotlib.org/)

## License

GPL-3.0-or-later
