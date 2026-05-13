import ffmpeg
import os
import shutil
from tools.unitman import bytes_to_mb

def check_ffmpeg():
    """Verifica que ffmpeg esté instalado y accesible"""
    for cmd in ["ffmpeg", "ffprobe"]:
        if not shutil.which(cmd):
            print(f"[!] {cmd} no está instalado o no está en PATH.")
            raise Exception(f"{cmd} no encontrado")

def get_media_info(input_file: str):
    """Obtiene tamaño, duracion, bitrate de video y bitrate de audio del archivo de entrada usando ffmpeg.probe"""
    try:
        probe = ffmpeg.probe(input_file)

        duration_s = int(round(float(probe['format']['duration'])))
        file_size_bytes = int(probe['format']['size'])
        file_size_mb = bytes_to_mb(file_size_bytes)

        # Buscar los streams de video y audio (no se usa posiciones absolutas para mayor robustez)
        video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        audio_stream = next(s for s in probe['streams'] if s['codec_type'] == 'audio')

        video_bitrate = int(video_stream['bit_rate']) // 1000
        audio_bitrate = int(audio_stream['bit_rate']) // 1000

        return file_size_mb, duration_s, video_bitrate, audio_bitrate
    except (ffmpeg.Error, ValueError, StopIteration) as e:
        print(f"Error: {e}")
        raise

def compress_video(input_file: str, output_file: str, target_video_bitrate_kbps: int, target_audio_bitrate_kbps: int):
    """Comprime el video usando ffmpeg con los bitrates objetivo para video y audio"""
    try:
        print ("PASS 1: Analyzing...")
        (
            ffmpeg
            .input(input_file)
            .output(
                os.devnull,
                vcodec='libx264',
                **{'b:v': f'{target_video_bitrate_kbps}k'},
                an=None,
                f='mp4',
                **{'pass': 1}
            )
            .overwrite_output()
            .global_args('-loglevel', 'error')
            .run()
        )

        print ("PASS 2: Compressing...")
        (
            ffmpeg
            .input(input_file)
            .output(
                output_file,
                vcodec='libx264',
                **{'b:v': f'{target_video_bitrate_kbps}k'},
                acodec='aac',
                **{'b:a': f'{target_audio_bitrate_kbps}k'},
                f='mp4',
                **{'pass': 2}
            )
            .overwrite_output()
            .global_args('-loglevel', 'error')
            .run()
        )
    except ffmpeg.Error as e:
        print(f"Error: {e}")