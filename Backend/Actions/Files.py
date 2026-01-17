import os
import shutil

def OpenFile(file_path):
    print(f"[Files] Opening: {file_path}")
    os.startfile(file_path)

def EditFile(file_path):
    print(f"[Files] Editing: {file_path}")
    os.system(f"notepad {file_path}")

def ReadFile(file_path):
    print(f"[Files] Reading: {file_path}")
    with open(file_path, 'r') as f:
        return f.read()

def CreateFile(data):
    try:
        file_path, content = data.split("|", 1)
        print(f"[Files] Creating: {file_path}")
        with open(file_path, 'w') as f:
            f.write(content)
    except ValueError:
        print(f"[Files] Invalid format for CreateFile: {data}")

def DeleteFile(file_path):
    print(f"[Files] Deleting: {file_path}")
    if os.path.exists(file_path):
        os.remove(file_path)

def CopyFile(data):
    src, dst = data.split("|")
    shutil.copy(src, dst)

def MoveFile(data):
    src, dst = data.split("|")
    shutil.move(src, dst)

def RenameFile(data):
    old, new = data.split("|")
    os.rename(old, new)

def ListFiles(directory="."):
    return os.listdir(directory)

def FileInfo(file_path):
    return os.stat(file_path)
