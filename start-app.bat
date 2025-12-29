@echo off
echo ========================================
echo 正在启动顺路带校园互助平台
echo ========================================

echo.
echo 正在启动后端服务...
start "后端服务" cmd /k "start-backend.bat"

echo.
echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo.
echo 正在启动前端服务...
start "前端服务" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ========================================
echo 启动完成！
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:9800
echo ========================================

echo.
echo 请稍等片刻，让服务完全启动后再访问前端页面。
pause