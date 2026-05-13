# ENCOGE - How it works

This document explains how the program works internally and how it converts a target file size into video and audio bitrates.

## 1. Core idea

ENCOGE does not guess the output bitrate directly from the input file size. It does this instead:

1. Reads the input file with `ffprobe`.
2. Gets the file size, duration, video bitrate and audio bitrate.
3. Uses the target size and overhead percentage to compute a total bitrate budget.
4. Subtracts the audio bitrate to obtain the video bitrate.
5. Encodes the video in two passes with `ffmpeg`.

The goal is to produce a file that stays close to the requested size while preserving as much quality as possible.

## 2. Units used by the program

This project uses binary units:

- `1 Byte = 8 bits`
- `1 kB = 1024 Bytes`
- `1 MB = 1024 kB`
- `1 MB = 8192 kbit`

That last value is the most important one for the calculations in the script.

$$1 \text{ MB} = 8192 \text{ kbit}$$

> Deduced with the formula:
> $$1 \text{ MB} = 1024 \text{ kB} \times 1024 \frac{\text{bytes}}{\text{kB}} \times 8 \frac{\text{bits}}{\text{byte}} = 8388608 \text{ bits} = 8192 \text{ kbit}$$

## 3. Bitrate concepts

### File bitrate

This is the average bitrate of the whole file, computed from file size and duration:

$$\text{file bitrate} = \frac{\text{file size in kbit}}{\text{duration in seconds}}$$

This value represents the mean bitrate of the complete container, not just the video stream.

### Stream bitrate

The program also reads:

- video bitrate
- audio bitrate

Those are the bitrates of the encoded streams themselves.

### Why they are not identical

The "file bitrate" and the sum of "video + audio bitrate" are usually close, but not equal. The difference comes from:

- container overhead
- metadata
- indexing structures
- rounding
- variable bitrate behavior

## 4. Overhead

MP4 and similar containers need extra space for internal data. This is called **overhead**.

The program reserves a percentage of the target size for that overhead before calculating the final bitrate budget.

$$\text{usable size} = \text{target size} \times (1 - \text{overhead})$$

Example with a 10 MB target and 5% overhead:

$$10 \times (1 - 0.05) = 9.7 \text{ MB}$$

That 9.7 MB is the size available for video and audio streams.

## 5. Target bitrate calculation

The program calculates the bitrate budget like this:

$$\text{target file bitrate} = \frac{\text{target size} \times (1 - \text{overhead}) \times 8192}{\text{duration}}$$

Then it subtracts the audio bitrate:

$$\text{target video bitrate} = \text{target file bitrate} - \text{target audio bitrate}$$

If audio bitrate is not explicitly provided, the program uses the audio bitrate from the original file.

## 6. Example

Suppose:

- duration = 120 s
- target size = 10 MB
- overhead = 3%
- audio bitrate = 128 kbps

First, calculate usable size:

$$10 \times 0.97 = 9.7 \text{ MB}$$

Convert that to kilobits:

$$9.7 \times 8192 = 79462.4 \text{ kbit}$$

Convert to total bitrate:

$$\frac{79462.4}{120} = 662.19 \text{ kbps}$$

Then subtract audio:

$$662.19 - 128 = 534.19 \text{ kbps}$$

So the program will target roughly:

- 662 kbps total:
  - 534 kbps video
  - 128 kbps audio

## 7. Two-pass encoding

ENCOGE uses two-pass encoding with `libx264`.

### Pass 1

The first pass analyzes the video and writes statistics for the second pass. No final output is kept.

### Pass 2

The second pass produces the final file using the analysis data from pass 1.

This improves bitrate distribution and quality compared with a single pass when the goal is to match a target size.

## 8. Program validations

The current implementation checks:

1. `ffmpeg` and `ffprobe` are installed
2. The input file exists
3. Overhead is between 0 and 1
4. The output file is valid
5. The output file does not already exist unless `-f` is used
6. The target video bitrate is not too low
7. The target size is not larger than the original file size

## 9. Practical interpretation

When you use ENCOGE, the important values are:

- **Target size**: the final goal in MB
- **Overhead**: reserved space for the container
- **Audio bitrate**: either user-defined or taken from the original file
- **Target video bitrate**: the remaining bitrate budget after audio is removed

If the target size is too small, the video bitrate can become impractically low. In that case, the resulting file will likely lose quality significantly, even if it technically fits the target.