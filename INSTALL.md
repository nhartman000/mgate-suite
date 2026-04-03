# Nych Installation Guide

## Windows One-Click Install
```
1. Download the repository
2. Double-click: install_windows.bat
3. Click Yes when prompted for admin rights
4. Wait for installation to complete
```

The installer will:
- Automatically install Python 3.12 if missing
- Install all dependencies
- Add Nych to system PATH
- Create desktop shortcut
- Verify installation

---

## Android APK Build

### Option 1: Build on Windows
```
cd android
build_apk.bat
```

### Option 2: Build directly on Android (Termux)
1. Install Termux from F-Droid
2. Run:
```bash
pkg update && pkg install python git openjdk-17
git clone https://github.com/nhartman000/mgate-suite
cd mgate-suite/android
pip install buildozer
buildozer android debug
```

APK will be created at `bin/Nych-1.0-arm64-v8a-debug.apk`

---

## Manual Installation
```bash
git clone https://github.com/nhartman000/mgate-suite
cd mgate-suite
pip install -r requirements.txt
python test_nych.py
```

---

## Usage
```bash
# Run project
python cli/run_project.py examples/project.mg8

# Test Nych subsystem
python test_nych.py
```
