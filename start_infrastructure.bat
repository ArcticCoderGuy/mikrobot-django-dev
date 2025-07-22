@echo off
echo Starting MikroBot MCP Production Infrastructure...
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo Please install Docker Desktop and make sure it's running.
    pause
    exit /b 1
)

echo Step 1: Creating logs directory...
if not exist logs mkdir logs

echo Step 2: Starting infrastructure services (Kafka + PostgreSQL + Redis)...
docker-compose up -d zookeeper kafka postgres redis

echo Step 3: Waiting for services to be healthy...
timeout /t 30 /nobreak >nul

echo Step 4: Creating Kafka topics...
docker exec mikrobot-kafka kafka-topics --create --topic pure-signals --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists
docker exec mikrobot-kafka kafka-topics --create --topic processed-signals --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists
docker exec mikrobot-kafka kafka-topics --create --topic trade-executions --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists
docker exec mikrobot-kafka kafka-topics --create --topic system-events --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists

echo Step 5: Starting Kafka UI (optional, for monitoring)...
docker-compose up -d kafka-ui

echo.
echo ========================================
echo MikroBot MCP Infrastructure Started!
echo ========================================
echo.
echo Services running:
echo - Kafka:        localhost:9092
echo - PostgreSQL:   localhost:5432
echo - Redis:        localhost:6379
echo - Kafka UI:     http://localhost:8080
echo.
echo Next steps:
echo 1. Install Python requirements: pip install -r requirements_production.txt
echo 2. Run migrations: python manage.py migrate --settings=mikrobot_mcp.settings_production
echo 3. Start MCP Agent: python mcp_agent/start_agent.py
echo.
echo Press any key to continue...
pause >nul