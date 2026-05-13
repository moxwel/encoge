from tools.args import parse_args
from tools.funcs import check_ffmpeg, get_media_info, compress_video, clear_logs
from tools.unitman import calculate_target_bitrate, MB_to_kbit, MB_to_kbps

def main():
    print("=== ENCOGE - BY MOXWEL ===")

    try:
        args = parse_args()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    check_ffmpeg()

    # get file info
    file_size_mb, file_dur_s, file_v_kbps, file_a_kbps = get_media_info(args.input_file)
    file_kbps = MB_to_kbps(file_size_mb, file_dur_s)
    overhead_p = args.overhead
    print("Input file:")
    print(f"    - Size                 : {file_size_mb} MB")
    print(f"    - Duration             : {file_dur_s} seconds")
    print(f"    - File bitrate         : {file_kbps} kbps (mean)")
    print(f"    - Video bitrate        : {file_v_kbps} kbps")
    print(f"    - Audio bitrate        : {file_a_kbps} kbps")
    print(f"    - Overhead             : {overhead_p * 100}%")

    # calculate target bitrates
    target_size_mb = args.target_size_mb
    target_a_kbps = args.target_audio_kbps if args.target_audio_kbps is not None else file_a_kbps # use original audio bitrate if not specified
    target_v_kbps, target_file_kbps = calculate_target_bitrate(target_size_mb, file_dur_s, overhead_p, target_a_kbps)
    print("Output file:")
    print(f"    - Target size          : {target_size_mb} MB (w/overhead {target_size_mb * (1 - overhead_p):.2f} MB)")
    print(f"    - Target file bitrate  : {target_file_kbps} kbps")
    print(f"    - Target video bitrate : {target_v_kbps} kbps")
    print(f"    - Target audio bitrate : {target_a_kbps} kbps")

    # dont allow target size higher than original (why?)
    if target_size_mb >= file_size_mb:
        print(f"Error: Target file size is higher than or equal to the original file size.")
        return 1

    # dont allow target video bitrate too low (ffmpeg limitation)
    if target_v_kbps <= 4:
        print(f"Error: Target video bitrate is too low. Please choose a larger target size or lower audio bitrate with -a.")
        return 1

    # warn if video bitrate is less than 50% of original
    if target_v_kbps <= file_v_kbps * 0.5:
        print(f"Warning: Target video bitrate is less than 50% of the original. This may result in significant quality loss.")

    print(f"Output file: {args.output}")

    if not args.probe:
        compress_video(args.input_file, args.output, target_v_kbps, target_a_kbps)
        clear_logs()
    else:
        print("Probe mode enabled. No compression will be performed.")

    print("Done.")
    return 0

if __name__ == "__main__":
    main()