import os

def check_file(path):
    if not os.path.exists(path):
        return
    try:
        with open(path, "rb") as f:
            content = f.read()
            if b"\x00" in content:
                print(f"!!! NULL BYTES DETECTED in {path} !!!")
                print(f"First 100 bytes: {content[:100]}")
            else:
                print(f"Clean: {path}")
    except Exception as e:
        print(f"Error reading {path}: {e}")

files_to_check = [
    "Main.py",
    "Verifer.py",
    "Backend/Automation.py",
    "Backend/Actions/Apps.py",
    "Backend/Actions/Files.py",
    "Backend/Actions/Web.py",
    "Backend/Actions/__init__.py",
    "Backend/__init__.py"
]

for f in files_to_check:
    check_file(f)
