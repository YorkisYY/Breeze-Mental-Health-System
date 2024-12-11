@echo off
echo Installing all required packages...

echo Installing PyInstaller...
pip install pyinstaller

echo Installing NumPy...
pip install numpy

echo Installing Pandas...
pip install pandas

echo Installing Matplotlib...
pip install matplotlib

echo Installing Tabulate...
pip install tabulate

echo Installing Colorama...
pip install colorama

echo All dependencies installed successfully!

echo Building executable using build_exe.py...
python build_exe.py

echo Build process completed!
pause
