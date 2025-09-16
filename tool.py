import os
import platform
import subprocess
import shutil
import hashlib

BASE_FOLDER = os.getcwd()
NEW_RSTM_FOLDER = os.path.join(BASE_FOLDER, "NEW_RSTM")
MOD_FOLDER = os.path.join(BASE_FOLDER, "MOD")
CONTENTS_FOLDER = os.path.join(BASE_FOLDER, "DAT_CONTENTS")
TOOLS_FOLDER = os.path.join(BASE_FOLDER, "external_tools")

if platform.system() == "Windows":
    ffmpeg_bin = os.path.join(TOOLS_FOLDER, "ffmpeg.exe")
else:
    ffmpeg_bin = "ffmpeg"

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
RESET = "\033[0m"

def file_hash(path):
    """Return SHA256 hash of a file (as hex)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def decompile_dats():
    if os.path.exists(os.path.join(BASE_FOLDER, "ASSETS.DAT")):
        print(f"{YELLOW}Decompiling ASSETS.DAT...{RESET}")
        subprocess.run(["python", os.path.join(TOOLS_FOLDER, "dave.py"), "X", "ASSETS.DAT", "-o", os.path.join(CONTENTS_FOLDER, "ASSETS")], check=True)

    if os.path.exists(os.path.join(BASE_FOLDER, "STREAMS.DAT")):
        print(f"{YELLOW}Decompiling STREAMS.DAT...{RESET}")
        subprocess.run(["python", os.path.join(TOOLS_FOLDER, "hash_build.py"), "X", "STREAMS.DAT", "-o", os.path.join(CONTENTS_FOLDER, "STREAMS"), "-nl", os.path.join(TOOLS_FOLDER, "STREAMS.LST"), "-a", "mclub", "-th", "45"])

def convert_to_wav():
    for file in os.listdir(NEW_RSTM_FOLDER):
        filename, ext = os.path.splitext(file)
        if ext.lower() != ".wav" and ext.lower() != ".rsm":
            ext_path = os.path.join(NEW_RSTM_FOLDER, f"{file}")
            filename, _ = os.path.splitext(file)
            wav_path = os.path.join(NEW_RSTM_FOLDER, f"{filename}.wav")
            print(f"Converting {file} → {filename}.wav")
            subprocess.run([
                ffmpeg_bin, '-y', '-i', ext_path,
                '-vn', '-sn', '-ac', '2', '-ar', '44100', '-acodec', 'pcm_s16le',
                wav_path
            ], check=True)
            os.remove(ext_path)

def convert_to_rstm():
    for file in os.listdir(NEW_RSTM_FOLDER):
        filename, ext = os.path.splitext(file)
        if ext.lower() == ".wav":
            wav_path = os.path.join(NEW_RSTM_FOLDER, f"{file}")
            filename, _ = os.path.splitext(file)
            print(f"Converting {file} → {filename}.rsm")
            subprocess.run(['python', os.path.join(TOOLS_FOLDER, "rstm_build.py"), wav_path], check=True)
            os.remove(wav_path)

def mod_dat():
    for folder in ["ASSETS", "STREAMS"]:
        mod_path = os.path.join(MOD_FOLDER, folder)
        target_path = os.path.join(CONTENTS_FOLDER, folder)

        if os.path.isdir(mod_path):
            print(f"{YELLOW}Applying mods from {mod_path} → {target_path}{RESET}")
            for root, dirs, files in os.walk(mod_path):
                rel_path = os.path.relpath(root, mod_path)
                dest_dir = os.path.join(target_path, rel_path)
                os.makedirs(dest_dir, exist_ok=True)

                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_dir, file)

                    if os.path.exists(dst_file):
                        if file_hash(src_file) == file_hash(dst_file):
                            print(f"{RED}{dst_file} is the same or was already modified.{RESET}")
                        else:
                            print(f"{YELLOW}Overwriting: {dst_file}{RESET}")
                    else:
                        print(f"{GREEN}Adding: {dst_file}{RESET}")

                    shutil.copy2(src_file, dst_file)

def compile_dats():
    print(f"{YELLOW}Compiling ASSETS.DAT...{RESET}")
    subprocess.run(["python", os.path.join(TOOLS_FOLDER, "dave.py"), "B", "-ca", "-cn", "-cf", "-fc", "1", f"{CONTENTS_FOLDER}/ASSETS", "ASSETS.DAT"], check=True)

    print(f"{YELLOW}Compiling STREAMS.DAT...{RESET}")
    subprocess.run(["python", os.path.join(TOOLS_FOLDER, "hash_build.py"), "B", f"{CONTENTS_FOLDER}/STREAMS", "STREAMS.DAT", "-a", "MClub"], check=True)

def main():
    answer = input(f"{BLUE}Do you want to decode STREAMS.DAT and ASSETS.DAT? {RESET}(Y/N) ").strip().lower()
    if answer == "y":
        decompile_dats()
    convert_to_wav()
    convert_to_rstm()
    mod_dat()
    answer = input(f"{BLUE}Do you want to encode STREAMS and ASSETS? {RESET}(Y/N) ").strip().lower()
    if answer == "y":
        compile_dats()
    

if __name__ == "__main__":
    main()