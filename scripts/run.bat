@echo off
echo ========================================
echo fault.watch Content Generator
echo ========================================
echo.
echo Choose an option:
echo   1. Generate all videos now
echo   2. Generate specific videos
echo   3. Start alert monitoring
echo   4. Organize content into dated folders
echo   5. Compile today's videos
echo   6. List content library
echo   7. Test single video
echo   8. Setup Windows Scheduler
echo   9. Exit
echo.

set /p choice="Enter choice (1-9): "

if "%choice%"=="1" (
    echo.
    echo Generating all videos...
    python generate_all.py
    python organize_content.py
)

if "%choice%"=="2" (
    echo.
    python generate_all.py --list
    echo.
    set /p nums="Enter script numbers (e.g., 1 5 7): "
    python generate_all.py %nums%
    python organize_content.py
)

if "%choice%"=="3" (
    echo.
    echo Starting alert monitor (Ctrl+C to stop)...
    python auto_generator.py
)

if "%choice%"=="4" (
    echo.
    echo Organizing content...
    python organize_content.py
)

if "%choice%"=="5" (
    echo.
    echo Compiling today's content...
    python compile_daily.py
)

if "%choice%"=="6" (
    echo.
    python organize_content.py --list
)

if "%choice%"=="7" (
    echo.
    python generate_all.py --list
    echo.
    set /p num="Enter script number to test: "
    python generate_all.py %num%
)

if "%choice%"=="8" (
    echo.
    echo Running scheduler setup (requires Admin)...
    powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1
)

if "%choice%"=="9" (
    exit
)

echo.
pause
