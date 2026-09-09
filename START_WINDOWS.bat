@echo off
echo ==========================================
echo AYU-RAKSHA IP - STARTUP
echo ==========================================
echo.
echo 1. Start backend in one terminal:
echo    cd backend
echo    .venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 2. Start frontend in a SECOND terminal:
echo    cd frontend
echo    npm install
echo    npm run dev
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:8000/docs
echo.
pause
