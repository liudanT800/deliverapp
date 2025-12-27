@echo off
echo 启动后端服务器...

REM 检查虚拟环境是否存在
if not exist .venv (
    echo 错误：未找到虚拟环境，请先运行 install-deps.bat
    pause
    exit /b 1
)

echo 激活虚拟环境...
call .venv\Scripts\activate

echo 设置开发环境变量...
set SECRET_KEY=change-me
set DATABASE_URL=sqlite+aiosqlite:///./test.db
set DEVELOPMENT_MODE=true

echo 启动服务器...
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause