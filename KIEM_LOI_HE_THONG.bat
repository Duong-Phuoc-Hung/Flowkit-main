@echo off
chcp 65001 > nul
echo ========================================================
echo       🚀 BỘ CÔNG CỤ KHÁM BỆNH HỆ THỐNG FLOWKIT V13.0
echo ========================================================
echo.

echo [1/4] Kiem tra loi cu phap Python (Flake8)...
call .\venv\Scripts\flake8 . --exclude=venv,flowkit-web/node_modules --count --select=E9,F63,F7,F82 --show-source --statistics
if %errorlevel% neq 0 (
    echo [!] Phat hien loi cu phap Python!
) else (
    echo [OK] Python sach se.
)
echo.

echo [2/4] Chay Kiem thu Tu dong Backend (Pytest)...
call .\venv\Scripts\pytest tests/
if %errorlevel% neq 0 (
    echo [!] Backend bi loi. Vui long xem chi tiet o tren.
) else (
    echo [OK] Backend hoat dong hoan hao.
)
echo.

echo [3/4] Kiem tra loi cu phap Frontend (Next.js ESLint)...
cd flowkit-web
call npm run lint
if %errorlevel% neq 0 (
    echo [!] Phat hien loi cu phap hoac canh bao tren Web UI!
) else (
    echo [OK] Web UI sach se.
)
echo.

echo [4/4] Chay Kiem thu Tu dong Frontend (Jest)...
call npm test
if %errorlevel% neq 0 (
    echo [!] Frontend UI bi loi. Vui long xem chi tiet o tren.
) else (
    echo [OK] Frontend UI hoat dong hoan hao.
)
cd ..
echo.

echo ========================================================
echo               HOAN THANH KIEM TRA!
echo ========================================================
pause
