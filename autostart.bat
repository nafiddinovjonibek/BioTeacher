@echo off
rem ---------------------------------------------------------------------------
rem BioTeacher — kompyuter yonganda serverni avtomatik ishga tushirish.
rem
rem   autostart.bat       ->  avtomatik ishga tushirishni YOQADI
rem   autostart.bat off   ->  O'CHIRADI
rem
rem Vazifa SYSTEM nomidan "tizim yonganda" ishlaydi: Windows ko'tarilishi bilan
rem server ko'tariladi — hech kim tizimga kirmasa ham, parol so'ralmaydi.
rem ---------------------------------------------------------------------------
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "TASK=BioTeacher"
set "ROOT=%~dp0"

rem --- Administrator huquqi kerak. Bo'lmasa — UAC orqali o'zini qayta chaqiradi.
net session >nul 2>&1
if not errorlevel 1 goto :admin
echo.
echo  Administrator huquqi kerak — ochilgan UAC oynasida "Ha" ni bosing.
if /i "%~1"=="off" goto :elevate_off
powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
exit /b
:elevate_off
powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -ArgumentList 'off' -Verb RunAs"
exit /b

:admin
if /i "%~1"=="off" goto :remove

echo.
echo  Vazifa yaratilmoqda: "%TASK%"  ^(tizim yonganda, SYSTEM nomidan^)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $r=('%ROOT%').TrimEnd('\'); $a=New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c run.bat 9999 service' -WorkingDirectory $r; $t=New-ScheduledTaskTrigger -AtStartup; $s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1); $p=New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest; Register-ScheduledTask -TaskName '%TASK%' -Action $a -Trigger $t -Settings $s -Principal $p -Description 'BioTeacher server, port 9999. Kompyuter yonganda avtomatik ishga tushadi.' -Force | Out-Null"
if errorlevel 1 goto :fail

echo  [OK] Bundan keyin kompyuter har yonganda server o'zi ishga tushadi.
echo.
echo   Hozir ishga tushirish:  schtasks /Run /TN "%TASK%"
echo   To'xtatish:             schtasks /End /TN "%TASK%"
echo   Holati:                 schtasks /Query /TN "%TASK%"
echo   Log:                    %ROOT%logs\autostart.log
echo   O'chirish:              autostart.bat off
echo.
echo  Eslatma: 9999-port band bo'lmasligi kerak — VS Code terminalida ishlab
echo           turgan serverni avval Ctrl+C bilan to'xtating.
goto :end

:remove
echo.
schtasks /End /TN "%TASK%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Unregister-ScheduledTask -TaskName '%TASK%' -Confirm:$false"
if errorlevel 1 goto :fail
echo  [OK] Avtomatik ishga tushirish o'chirildi.
goto :end

:fail
echo.
echo  [X] Bajarilmadi — yuqoridagi xabarni o'qing.
pause
exit /b 1

:end
echo.
pause
