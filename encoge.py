from tools.args import parse_args
from tools.funcs import check_ffmpeg, get_media_info, compress_video
from tools.unitman import calculate_target_bitrate, mb_to_kbits, mb_to_kbps

def main():
    print("=== ENCOGE - BY MOXWEL ===")

    try:
        args = parse_args()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    check_ffmpeg()

    file_size_mb, file_dur_s, file_v_kbps, file_a_kbps = get_media_info(args.input_file)
    file_kbps = mb_to_kbps(file_size_mb, file_dur_s)
    print("Input file:")
    print(f"    - Size          : {file_size_mb} MB")
    print(f"    - Duration      : {file_dur_s} seconds")
    print(f"    - File bitrate  : {file_kbps} kbps (mean)")
    print(f"    - Video bitrate : {file_v_kbps} kbps")
    print(f"    - Audio bitrate : {file_a_kbps} kbps")



    target_size_mb = args.target_size_mb
    overhead_p = args.overhead
    target_a_kbps = args.target_audio_kbps if args.target_audio_kbps is not None else file_a_kbps
    print("Target:")
    print(f"    - Size          : {target_size_mb} MB")
    print(f"    - Overhead      : {overhead_p * 100}%")
    print(f"    - Audio bitrate : {target_a_kbps} kbps")


    target_v_kbps, target_file_kbps = calculate_target_bitrate(target_size_mb, file_dur_s, overhead_p, target_a_kbps)
    print("Calculated:")
    print(f"    - Target file bitrate : {target_file_kbps} kbps")
    print(f"    - Target video bitrate: {target_v_kbps} kbps")

    if target_v_kbps <= 4:
        print(f"Error: Target video bitrate is too low. Please choose a larger target size or lower audio bitrate with -a.")
        return 1

    print(f"Output file: {args.output}")
    compress_video(args.input_file, args.output, target_v_kbps, target_a_kbps)


if __name__ == "__main__":
    main()