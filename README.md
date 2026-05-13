<div align="center">
  <img src="./img/banner.png" alt="ENCOGE banner" width="150">
    <h1>ENCOGE</h1>
</div>

ENCOGE is a small Python tool that **compresses a video to a target file size** using two-pass `libx264` encoding. It calculates the bitrate budget automatically from the requested size, duration, audio bitrate, and overhead.

In other words, you can say **"I want this video to be around 10 MB"** and ENCOGE will do its best to meet that target while preserving quality.

## What it does?

- reads the input file with `ffprobe`
- estimates the file size, duration, video bitrate, and audio bitrate
- computes a target bitrate budget from the requested output size
- subtracts the audio bitrate to obtain the video bitrate
- runs a two-pass `ffmpeg` encode
- removes temporary two-pass log files after encoding

> [!NOTE]
> If you want the mathematical background, unit conversions, and bitrate formulas, see [LEARN.md](./LEARN.md).

## Why?

I wanted to share game clips to my friends in Discord, but the original files were too large. I needed a quick way to compress them to a specific size without losing too much quality. I also wanted to learn how to use `ffmpeg` and `ffprobe` from Python.

## Requirements

- Python 3.6 or newer
- `ffmpeg` in `PATH`
- `ffprobe` in `PATH`
- `ffmpeg-python` installed in the active Python environment

### Installation

Install `ffmpeg` (and `ffprobe`) in your system using your package manager or from the [official website](https://ffmpeg.org/download.html).

Install the Python dependency with:

```bash
pip install ffmpeg-python
```

Or create a virtual environment and install there:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python encoge.py <input_file> [options]
```

### Options

| Option | Description | Default |
|---|---|---|
| `-t`, `--target_size_mb` | Target output size in MB | `10` |
| `-O`, `--overhead` | Reserved percentage for container overhead | `0.05` |
| `-o`, `--output` | Output file name | `<input_name>__COMP.<ext>` |
| `-a`, `--target_audio_kbps` | Target audio bitrate in kbps | Original audio bitrate |
| `-f`, `--force` | Overwrite output file if it already exists | `false` |
| `-p`, `--probe` | Probe the file and print information without compressing | `false` |

### Examples

Compress a video to the default target size:

```bash
python encoge.py video.mp4
```

Compress to 50 MB:

```bash
python encoge.py video.mp4 -t 50
```

Set a custom output file:

```bash
python encoge.py video.mp4 -t 25 -o output.mp4
```

Use a custom audio bitrate:

```bash
python encoge.py video.mp4 -t 15 -a 128
```

Probe only, without encoding:

```bash
python encoge.py video.mp4 -p
```

Force overwrite if the output file already exists:

```bash
python encoge.py video.mp4 -f
```

## Output naming

If `-o` is not provided, ENCOGE creates the output name from the input file name and appends `__COMP` before the extension.

Examples:

- `video.mp4` -> `video__COMP.mp4`
- `clip.mkv` -> `clip__COMP.mkv`

If `-o` is provided:

- `-o mivideo.mp4` -> output file is `mivideo.mp4`
- `-o mivideo` -> the parser expects an extension and will reject the name

## Typical workflow

1. Run ENCOGE with `-p` to inspect the input file.
2. Adjust the target size, overhead, or audio bitrate if needed.
3. Run the compression step.
4. Review the output file and repeat with a different target if necessary.

## Behavior notes

- The program uses two-pass encoding for better bitrate allocation.
- The first pass analyzes the video and writes temporary log files.
- The second pass produces the final compressed file.
- Temporary files such as `ffmpeg2pass-0.log*` are removed after a successful encode.
- If the target video bitrate is too low, the program stops instead of producing a file with unusable quality.

## Project layout

- `encoge.py` - main entry point and orchestration
- `tools/args.py` - command-line argument parsing and validation
- `tools/funcs.py` - media probing, compression, and cleanup helpers
- `tools/unitman.py` - unit conversion helpers
- `LEARN.md` - technical notes and formulas
