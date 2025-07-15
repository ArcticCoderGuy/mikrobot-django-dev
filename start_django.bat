@echo off
echo Starting MikroBot Django Development Environment...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Virtual environment activated!
echo.
echo Available Django commands:
echo   python manage.py runserver       - Start development server
echo   python manage.py makemigrations  - Create database migrations
echo   python manage.py migrate         - Apply database migrations
echo   python manage.py createsuperuser - Create admin user
echo   python manage.py shell           - Open Django shell
echo   python manage.py test            - Run tests
echo.
echo Environment ready! Type your commands below:
echo.

REM Keep the command prompt open
cmd /k