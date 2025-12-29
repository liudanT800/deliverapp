@echo off
echo ========================================
echo 正在启动顺路带校园互助平台
echo ========================================

echo.
echo 正在启动后端服务...
start "后端服务" cmd /k "cd backend && python -m venv .venv 2>nul && .venv\Scripts\activate && set SECRET_KEY=change-me && set DATABASE_URL=sqlite+aiosqlite:///./test.db && set DEVELOPMENT_MODE=true && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo.
echo 正在启动前端服务...
start "前端服务" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ========================================
echo 启动完成！
echo 前端地址: http://localhost:4173
echo 后端地址: http://localhost:8000
echo ========================================

echo.
echo 请稍等片刻，让服务完全启动后再访问前端页面。
pause