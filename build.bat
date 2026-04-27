@echo off
echo === FB Auto Post Tool — PyInstaller build ===
echo.

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building FBAutoPost.exe...
pyinstaller --onefile --windowed ^
  --name "FBAutoPost" ^
  --add-data "src;src" ^
  --collect-all streamlit ^
  --collect-all streamlit_option_menu ^
  --collect-all streamlit_extras ^
  src\main.py

echo.
echo Copying support files...
if exist .env.example copy .env.example dist\
if exist README.md copy README.md dist\

echo.
echo Done. Output: dist\FBAutoPost.exe
pause
