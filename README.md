# ir-cleanup

A command-line tool to truncate impulse response (IR) audio files based on energy content.

## What it does

Given an IR file, the tool:

1. Detects the peak sample and trims any leading content before it
2. Finds the point where the signal has accumulated a given percentage of its total energy
3. Cuts the IR at that point
4. Applies a linear fade-out at the end to avoid a hard cutoff
5. Plots the waveform and cumulative energy curve with the cut point highlighted

This reduces reverb tail length while retaining a configurable amount of the original energy.

## Installation

```bash
pip install .
```

## Usage

```bash
ir_cleanup [options] <input> <output> <energy_percent>
```

| Argument | Description |
|---|---|
| `input` | Input IR file (WAV, FLAC, AIFF, OGG, ...) |
| `output` | Output truncated IR file |
| `energy_percent` | Energy to retain, strictly between 0 and 100 (e.g. `99.9`) |

### Options

| Option | Description |
|---|---|
| `--fade-length MS` | Fade-out duration in milliseconds (default: 256 samples) |
| `--no-plot` | Skip the plot display |
| `--save-plot FILE` | Save the plot to FILE (can be combined with `--no-plot`) |

### Examples

```bash
# Basic usage
ir_cleanup room.wav room_truncated.wav 99.9

# Custom fade-out of 10 ms, save plot without displaying it
ir_cleanup room.flac room_truncated.flac 99.5 --fade-length 10 --no-plot --save-plot room.png
```

## Notes

- Multi-channel files are supported: the energy analysis uses a mono downmix internally, but the cut point is applied to all channels and the output preserves the original channel count.
- Input and output formats are determined by the file extension. Any format supported by [libsndfile](http://www.mega-nerd.com/libsndfile/) works (WAV, FLAC, AIFF, OGG, ...).
- The sample rate is preserved from the input file.

## Dependencies

- [numpy](https://numpy.org/)
- [soundfile](https://python-soundfile.readthedocs.io/)
- [matplotlib](https://matplotlib.org/)

## License

GPL-3.0-or-later
