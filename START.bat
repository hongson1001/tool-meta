@echo off
title FB Auto Post Tool

echo ================================================
echo   FB AUTO POST TOOL
echo ================================================
echo.

REM Check Python
where py >nul 2>&1
if errorlevel 1 goto NO_PYTHON

REM Setup venv neu chua co
if not exist venv\Scripts\activate.bat goto SETUP_VENV
goto SETUP_ENV

:NO_PYTHON
echo [LOI] Chua cai dat Python. Hay cai Python 3.11 tu:
echo       https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
echo.
echo Nho TICK "Add Python to PATH" khi cai.
pause
exit /b 1

:SETUP_VENV
echo [SETUP] Lan dau chay - dang cai dat moi truong...
py -3.11 -m venv venv
if errorlevel 1 goto VENV_FAIL
echo [SETUP] Dang cai thu vien - mat 3 den 5 phut...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 goto PIP_FAIL
goto SETUP_ENV

:VENV_FAIL
echo [LOI] Khong tao duoc venv. Hay dam bao Python 3.11 da cai.
pause
exit /b 1

:PIP_FAIL
echo [LOI] Cai thu vien that bai.
pause
exit /b 1

:SETUP_ENV
if exist .env goto RUN_TOOL
echo [SETUP] Tao file .env tu .env.example
copy .env.example .env > nul
echo.
echo ================================================
echo Hay mo file .env va dien thong tin sau:
echo   - FB_APP_ID, FB_APP_SECRET tu Facebook Developer
echo   - GOOGLE_SHEET_ID tu URL Google Sheet
echo Sau do tai file credentials.json tu Google Cloud
echo va luu vao thu muc data\
echo Doc SETUP.md de biet huong dan chi tiet.
echo ================================================
pause

:RUN_TOOL
call venv\Scripts\activate.bat
echo.
echo [DANG CHAY] Tool dang khoi dong... Browser se mo trong vai giay.
echo Khi muon tat tool, dong cua so nay hoac bam Ctrl+C.
echo.
streamlit run src\ui\app.py --server.headless true --browser.gatherUsageStats false
pause
