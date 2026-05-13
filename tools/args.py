import argparse
from pathlib import Path

def parse_args():
    arg_parser = argparse.ArgumentParser(description="Compress video file to target size.")
    arg_parser.add_argument("input_file", help="Input video file")
    arg_parser.add_argument("--target_size_mb", "-t", type=int, default=10, help="Target size in MB. Default is 10 MB.")
    arg_parser.add_argument("--overhead", "-O", type=float, default=0.05, help="Overhead percentage (0 - 1). Default is 0.05.")
    arg_parser.add_argument("--output", "-o", type=str, default=None, help="Output file name w/ extension. Default is <filename>__COMP.<ext>")
    arg_parser.add_argument("--target_audio_kbps", "-a", type=int, default=None, help="Target audio bitrate in kbps. Default is original audio bitrate.")
    arg_parser.add_argument("--force", "-f", action="store_true", help="Force overwrite of output file if it exists.")
    arg_parser.add_argument("--probe", "-p", action="store_true", help="Only probe the input file and print its info without compressing.")
    args = arg_parser.parse_args()

    # input file is valid?
    input_path = Path(args.input_file)
    if not input_path.is_file():
        raise ValueError(f"Input file '{args.input_file}' does not exist or is not a file.")

    # overhead percentage is valid?
    if args.overhead < 0 or args.overhead >= 1:
        raise ValueError("Overhead percentage must be between 0 and 1 (exclusive).")

    # handle output file name
    # append __COMP to input file name if output is not specified
    if args.output is None:
        input_path = Path(args.input_file)
        args.output = f"{input_path.stem}__COMP{input_path.suffix}"
    else:
        output_path = Path(args.output)
        if output_path.is_dir():
            raise ValueError("Output path cannot be a directory.")
        if not output_path.suffix:
            raise ValueError("Output file must have an extension.")

    # output file exists?
    output_path = Path(args.output)
    if output_path.exists():
        if not args.force:
            raise ValueError(f"Output file '{args.output}' already exists. Please choose a different name or remove the existing file. Use -f to force overwrite.")

    return args