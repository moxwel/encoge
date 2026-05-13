from math import floor

'''
kb = kilobytes
mb = megabytes
kbits = kilobits
kbps = kilobits por segundo
'''

def bytes_to_kb(bytes: int):
    """Convierte bytes a kilobytes (base 2)"""
    return bytes // 1024

def kb_to_mb(kb: int):
    """Convierte kilobytes a megabytes (base 2)"""
    return kb // 1024

def bytes_to_mb(bytes: int):
    """Convierte bytes a megabytes (base 2)"""
    return kb_to_mb(bytes_to_kb(bytes))

def mb_to_kbits(mb: int):
    """Convierte megabytes a kilobits (base 2)"""
    return mb * 8192

def kbits_to_kbps(kbits: int, duration_s: int):
    """Convierte kilobits a kilobits por segundo dado una duración en segundos"""
    return kbits // duration_s

def mb_to_kbps(mb: int, duration_s: int):
    """Convierte megabytes a kilobits por segundo dado una duración en segundos"""
    return kbits_to_kbps(mb_to_kbits(mb), duration_s)

def calculate_target_bitrate(target_size_mb: int, duration_s: int, overhead_p: float, audio_kbps: int):
    """Calcula los bitrates objetivo para video y audio dado el tamaño objetivo, duración, overhead y bitrate de audio"""
    target_kbits = mb_to_kbits(floor(target_size_mb * (1 - overhead_p)))
    target_kbps = kbits_to_kbps(target_kbits, duration_s)
    target_v_kbps = target_kbps - audio_kbps
    return target_v_kbps, target_kbps
