@echo off
rem ---------------------------------------------------------------------------
rem BioTeacher — lokal serverni ishga tushirish.
rem
rem   run.bat              ->  0.0.0.0:9999  (lokal: http://127.0.0.1:9999/ , tashqi: najo.uz)
rem   run.bat 8000         ->  boshqa portda
rem   run.bat 9999 service ->  avtomatik rejim: xato bo'lsa ham oynani kutib turmaydi
rem                            (autostart.bat yaratgan vazifa shu rejimda chaqiradi)
rem ---------------------------------------------------------------------------
setlocal
chcp 65001 >nul
cd /d "%~dp0"

rem 0.0.0.0 — tashqi so'rovlar ham qabul qilinadi (najo.uz shu portga yo'naltirilgan).
rem Faqat shu kompyuterdan ochish uchun: HOST=127.0.0.1.
set "HOST=0.0.0.0"

set "PORT=%~1"
if "%PORT%"=="" set "PORT=9999"

rem Vazifa rejalashtiruvchisi ostida oyna bo'lmaydi — `pause` abadiy kutib qolmasligi kerak.
set "SERVICE="
if /i "%~2"=="service" set "SERVICE=1"

set "PY=%CD%\env\Scripts\python.exe"
if not exist "%PY%" (
    echo.
    echo  [X] Virtual muhit topilmadi: %PY%
    echo      Avval bir marta bajaring:
    echo          python -m venv env
    echo          env\Scripts\pip install -r requirements.txt
    echo.
    if not defined SERVICE pause
    exit /b 1
)

echo.
echo  BioTeacher  --^>  http://127.0.0.1:%PORT%/   ^(bind: %HOST%:%PORT%^)
echo  To'xtatish: Ctrl+C
echo.

if defined SERVICE (
    rem Avtomatik rejimda oyna yo'q — chiqish logga yoziladi (har yonganda yangilanadi).
    "%PY%" manage.py runserver %HOST%:%PORT% > "%CD%\logs\autostart.log" 2>&1
) else (
    "%PY%" manage.py runserver %HOST%:%PORT%
)
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
    echo.
    echo  [X] Server xato bilan to'xtadi ^(kod: %RC%^).
    if not defined SERVICE pause
)
exit /b %RC%
