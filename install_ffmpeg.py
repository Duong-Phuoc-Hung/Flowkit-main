#!/usr/bin/env python3
"""
install_ffmpeg.py — Auto-install ffmpeg for FlowKit
=====================================================
Supports: Windows, macOS, Linux

Usage:
    python install_ffmpeg.py

Options:
    --method winget|choco|scoop|manual   Force a specific install method (Windows)
    --dir <path>                         Install to specific directory (manual download)
    --check                              Only check if ffmpeg is installed
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
import tempfile

FFMPEG_VERSION_URL = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"
FFMPEG_WIN_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_LINUX_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")

def check_ffmpeg():
    """Check if ffmpeg is already installed and accessible."""
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
            )
            version_line = result.stdout.splitlines()[0] if result.stdout else "unknown"
            log(f"? ffmpeg already installed: {version_line}", GREEN)
            log(f"   ffmpeg  ? {ffmpeg}", GREEN)
            log(f"   ffprobe ? {ffprobe}", GREEN)
            return True
        except Exception:
            pass
    return False

def run_cmd(cmd, check=True):
    """Run a shell command and return True on success."""
    log(f"  ? {' '.join(cmd)}", CYAN)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return True
        if check:
            log(f"  Error: {result.stderr.strip()}", RED)
        return False
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        log("  Timeout!", RED)
        return False

# --- Windows installers --------------------------------------------------------

def install_via_winget():
    log("\n?? Trying winget...", CYAN)
    if run_cmd(["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--accept-source-agreements", "--accept-package-agreements"]):
        log("? Installed via winget!", GREEN)
        return True
    log("??  winget failed or not available.", YELLOW)
    return False

def install_via_choco():
    log("\n?? Trying Chocolatey (choco)...", CYAN)
    if run_cmd(["choco", "install", "ffmpeg", "-y"]):
        log("? Installed via Chocolatey!", GREEN)
        return True
    log("??  Chocolatey failed or not installed.", YELLOW)
    return False

def install_via_scoop():
    log("\n?? Trying Scoop...", CYAN)
    if run_cmd(["scoop", "install", "ffmpeg"]):
        log("? Installed via Scoop!", GREEN)
        return True
    log("??  Scoop failed or not installed.", YELLOW)
    return False

def install_manual_windows(install_dir=None):
    """Download ffmpeg zip from BtbN/FFmpeg-Builds and extract to install_dir."""
    if install_dir is None:
        install_dir = os.path.dirname(os.path.abspath(__file__))

    log(f"\n?? Downloading ffmpeg (manual) ? {install_dir} ...", CYAN)
    log(f"   Source: {FFMPEG_WIN_URL}", CYAN)

    zip_path = os.path.join(tempfile.gettempdir(), "ffmpeg_win.zip")

    try:
        log("   Downloading... (this may take 1-2 minutes)", YELLOW)
        urllib.request.urlretrieve(FFMPEG_WIN_URL, zip_path)
        log("   Extracting...", YELLOW)

        with zipfile.ZipFile(zip_path, "r") as zf:
            # Find the bin/ folder inside the zip
            bin_members = [m for m in zf.namelist() if "/bin/" in m and m.endswith(".exe")]
            if not bin_members:
                log("   ? Could not find .exe files in zip!", RED)
                return False

            for member in bin_members:
                filename = os.path.basename(member)
                dest = os.path.join(install_dir, filename)
                with zf.open(member) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                log(f"   Extracted ? {dest}", GREEN)

        # Verify
        ffmpeg_path = os.path.join(install_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_path):
            log(f"\n? ffmpeg installed to: {install_dir}", GREEN)
            log(f"   Add this directory to PATH if not already present.", YELLOW)
            _add_to_path_windows(install_dir)
            return True
    except Exception as e:
        log(f"   ? Download/extract failed: {e}", RED)
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)
    return False

def _add_to_path_windows(directory):
    """Add a directory to the current process PATH."""
    current_path = os.environ.get("PATH", "")
    if directory.lower() not in current_path.lower():
        os.environ["PATH"] = directory + os.pathsep + current_path
        log(f"   Added to current session PATH: {directory}", YELLOW)
        log(f"   ??  To persist, add manually to System Environment Variables.", YELLOW)

# --- macOS installer ----------------------------------------------------------

def install_macos():
    log("\n?? macOS detected.", CYAN)

    # Try Homebrew
    log("   Trying Homebrew (brew)...", CYAN)
    if run_cmd(["brew", "install", "ffmpeg"]):
        log("? Installed via Homebrew!", GREEN)
        return True

    log("   Homebrew not found. Install it from https://brew.sh, then re-run.", YELLOW)
    log("   Or install ffmpeg manually: https://evermeet.cx/ffmpeg/", YELLOW)
    return False

# --- Linux installer ----------------------------------------------------------

def install_linux():
    log("\n?? Linux detected.", CYAN)

    # apt (Debian/Ubuntu)
    if shutil.which("apt-get"):
        log("   Trying apt-get...", CYAN)
        run_cmd(["sudo", "apt-get", "update", "-qq"], check=False)
        if run_cmd(["sudo", "apt-get", "install", "-y", "ffmpeg"]):
            log("? Installed via apt-get!", GREEN)
            return True

    # dnf (Fedora/RHEL)
    if shutil.which("dnf"):
        log("   Trying dnf...", CYAN)
        if run_cmd(["sudo", "dnf", "install", "-y", "ffmpeg"]):
            log("? Installed via dnf!", GREEN)
            return True

    # pacman (Arch)
    if shutil.which("pacman"):
        log("   Trying pacman...", CYAN)
        if run_cmd(["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"]):
            log("? Installed via pacman!", GREEN)
            return True

    log("   ? Could not auto-install on this Linux distro.", RED)
    log("   Please install ffmpeg manually: https://ffmpeg.org/download.html", YELLOW)
    return False

# --- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Auto-install ffmpeg for FlowKit")
    parser.add_argument("--method", choices=["winget", "choco", "scoop", "manual"],
                        help="Force a specific install method (Windows only)")
    parser.add_argument("--dir", help="Target directory for manual download (Windows only)")
    parser.add_argument("--check", action="store_true", help="Only check if ffmpeg is installed")
    args = parser.parse_args()

    log("\n?? FlowKit — ffmpeg Installer", CYAN)
    log("=" * 40, CYAN)

    # Check first
    if check_ffmpeg():
        if args.check:
            sys.exit(0)
        log("\nffmpeg is already installed. Nothing to do!", GREEN)
        sys.exit(0)

    if args.check:
        log("\n? ffmpeg is NOT installed.", RED)
        sys.exit(1)

    system = platform.system()
    log(f"\n??  OS: {system} ({platform.machine()})", CYAN)

    success = False

    if system == "Windows":
        if args.method == "winget" or not args.method:
            success = install_via_winget()
        if not success and (args.method == "choco" or not args.method):
            success = install_via_choco()
        if not success and (args.method == "scoop" or not args.method):
            success = install_via_scoop()
        if not success and (args.method == "manual" or not args.method):
            success = install_manual_windows(args.dir)

    elif system == "Darwin":
        success = install_macos()

    elif system == "Linux":
        success = install_linux()

    else:
        log(f"? Unsupported OS: {system}", RED)
        sys.exit(1)

    # Final verification
    log("\n?? Verifying installation...", CYAN)
    if success and check_ffmpeg():
        log("\n?? ffmpeg is ready! You can now run FlowKit.", GREEN)
        sys.exit(0)
    else:
        log("\n? ffmpeg installation failed or not found in PATH.", RED)
        log("Please install manually: https://ffmpeg.org/download.html", YELLOW)
        log("Windows guide: https://www.gyan.dev/ffmpeg/builds/", YELLOW)
        sys.exit(1)

if __name__ == "__main__":
    main()
