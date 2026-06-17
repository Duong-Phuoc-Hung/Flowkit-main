@echo off
title FlowKit AI Studio V14.0 Pro - AUTO MODE
color 0A
echo ==================================================
echo         FLOWKIT AI STUDIO PRO (V14.0 ULTIMATE)
echo              CHE DO TU DONG 100%
echo ==================================================
echo.
echo [1/3] Dang khoi dong Giao Dien Chuyen Nghiep (Electron)...
cd flowkit-web
start "" cmd /c "npm run app"
cd ..

echo [2/3] Dang bat Cung Cap Nang Luong AI (Background Worker)...
start "" .\venv\Scripts\python auto_factory.py

echo [3/3] Dang ket noi Truc tiep Google Flow (Backend Server)...
echo.
echo Vui long KHONG TAT cua so mau den nay! Ban co the thu nho no xuong.
echo.
.\venv\Scripts\python -m agent.main

pause
