import subprocess
# pip install openai-whisper

def extract_audio(video_path, output_wav='audio.wav'):
    command = [
        'ffmpeg',
        '-y',   # 덮어쓰기 허용
        '-i', video_path,
        '-vn', # 영상 제거
        '-acodec', 'pcm_s16le', # wav 코덱
        '-ar', '16000', # 샘플링 Hz
        '-ac', '1', # 모노
        output_wav
    ]
    subprocess.run(command, check=True)
    print(f"f오디오 추출 완료:{output_wav}")
    return output_wav
if __name__ == '__main__':
    audio_file = extract_audio("sample.mp4")