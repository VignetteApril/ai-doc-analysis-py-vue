@echo off
REM AI Document Analysis System - Stop Development Environment Script (Windows)
REM Used to stop all development services

echo Stopping AI Document Analysis System development environment
echo =============================================

REM Check if in project root directory
if not exist "docker-compose.yml" (
    echo ERROR: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Stop backend service
echo Stopping backend service...
docker-compose down

echo Development environment stopped successfully
pause