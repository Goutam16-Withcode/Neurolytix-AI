@echo off
echo ========================================================
echo         Launching Neurolytix AI Full-Stack Studio
echo ========================================================
echo.

:: Launch FastAPI Backend Server
echo [1/2] Starting Python FastAPI Backend on http://localhost:8000 ...
start "Neurolytix Backend API" cmd /k "python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload"

:: Launch Next.js Web Frontend
echo [2/2] Starting Next.js Web Frontend on http://localhost:3000 ...
start "Neurolytix Next.js UI" cmd /k "cd web && npm run dev"

echo.
echo Both servers have been launched!
echo Open your browser to http://localhost:3000 to access the studio.
echo.
pause
