import os
import shutil
import subprocess

def clean_build():
    # Remove build directory if exists
    if os.path.exists('build'):
        shutil.rmtree('build')
    print("Build directory cleaned")

def build_exe():
    # Run PyInstaller
    subprocess.run(['pyinstaller', 'breeze.spec'])
    
    # Copy emotion_model.pkl to dist folder
    shutil.copy('emotion_model.pkl', 'dist/emotion_model.pkl')
    print("Copied emotion_model.pkl to dist folder")
    
    # Clean up build folder
    # clean_build()

if __name__ == "__main__":
    build_exe()
