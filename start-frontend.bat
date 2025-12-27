@echo off
cd frontend
echo Installing frontend dependencies...
call npm install
echo Starting frontend service...
call npm run dev
pause