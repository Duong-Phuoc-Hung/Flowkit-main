@echo off
title Khoi Phuc Icon Desktop
color 0E
echo ==================================================
echo     DANG TAO LAI ICON RA NGOAI MAN HINH CHINH
echo ==================================================
echo.

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Desktop = [Environment]::GetFolderPath('Desktop'); $Shortcut = $WshShell.CreateShortcut($Desktop + '\FlowKit AUTO.lnk'); $Shortcut.TargetPath = '%~dp0CHAY_TU_DONG.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save(); $Shortcut2 = $WshShell.CreateShortcut($Desktop + '\FlowKit MANUAL.lnk'); $Shortcut2.TargetPath = '%~dp0KHOI_DONG_APP.bat'; $Shortcut2.WorkingDirectory = '%~dp0'; $Shortcut2.Save();"

echo Hoan tat! 2 Icon "FlowKit AUTO" va "FlowKit MANUAL" da duoc tao lai tren Desktop.
echo.
pause
