@echo off
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean ^
  --name "PinIt" ^
  --windowed ^
  --onedir ^
  --add-data "assets;assets" ^
  main.py
echo Build finished. See dist\PinIt\PinIt.exe
pause
