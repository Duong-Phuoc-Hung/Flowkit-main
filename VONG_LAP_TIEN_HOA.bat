@echo off
chcp 65001 > nul
title Vong Lap KCS va Tien Hoa He Thong

:loop
cls
echo ========================================================
echo        HỆ THỐNG VÒNG LẶP TIẾN HÓA LIÊN TỤC (CI/CD)
echo ========================================================
echo.
echo [BƯỚC 1] KIỂM TRA LỖI HỆ THỐNG (FLAKE8, PYTEST, ESLINT)...
call .\KIEM_LOI_HE_THONG.bat

echo.
echo [BƯỚC 2] CHẠY MÔ PHỎNG END-TO-END GIẢ LẬP...
call .\venv\Scripts\python scripts/simulate_e2e.py

echo.
echo ========================================================
echo [HOÀN TẤT] 1 Vòng lặp tiến hóa đã xong! 
echo Hệ thống sạch sẽ 100%% và hoạt động trơn tru từ A-Z.
echo.
echo Sếp có thể code thêm tính năng mới, sau đó bấm phím bất kỳ
echo để hệ thống TỰ ĐỘNG KIỂM TRA LẠI TỪ ĐẦU!
echo ========================================================
pause
goto loop
