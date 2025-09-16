import os
import platform
import subprocess

BASE_FOLDER = os.getcwd()
REPLACE_FOLDER = os.path.join(BASE_FOLDER, "REPLACE")
TOOLS_FOLDER = os.path.join(BASE_FOLDER, "external_tools")

if platform.system() == "Windows":
    ffmpeg_bin = os.path.join(TOOLS_FOLDER, "ffmpeg.exe")
else:
    ffmpeg_bin = "ffmpeg"


for file in os.listdir(REPLACE_FOLDER):
    filename, ext = os.path.splitext(file)
    if ext.lower() != ".wav" and ext.lower() != ".rsm":
        ext_path = os.path.join(REPLACE_FOLDER, f"{file}")
        filename, _ = os.path.splitext(file)
        wav_path = os.path.join(REPLACE_FOLDER, f"{filename}.wav")
        print(f"Converting {file} → {filename}.wav")
        subprocess.run([
            ffmpeg_bin, '-y', '-i', ext_path,
            '-vn', '-sn', '-ac', '2', '-ar', '44100', '-acodec', 'pcm_s16le',
            wav_path
        ], check=True)
        os.remove(ext_path)

for file in os.listdir(REPLACE_FOLDER):
    filename, ext = os.path.splitext(file)
    if ext.lower() == ".wav":
        wav_path = os.path.join(REPLACE_FOLDER, f"{file}")
        filename, _ = os.path.splitext(file)
        print(f"Converting {file} → {filename}.rsm")
        subprocess.run(['python', os.path.join(TOOLS_FOLDER, "rstm_build.py"), wav_path], check=True)
        os.remove(wav_path)