@echo off
cd backend
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
)
echo Installing/updating dependencies...
pip install -r requirements.txt
echo Starting backend service...
set SECRET_KEY=change-me
set DATABASE_URL=sqlite+aiosqlite:///./test.db
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9800
pause