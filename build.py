import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--name", "compwesr",
    "--paths", "src",
    "--collect-all", "imageio_ffmpeg",
    "main.py",
], check=True)
