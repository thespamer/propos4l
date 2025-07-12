#!/bin/sh

# Function to check if a service is ready
wait_for_service() {
    host="$1"
    port="$2"
    service_name="$3"
    max_retries=60
    retries=0

    echo "Waiting for $service_name to be ready at $host:$port..."
    
    # Try to ping the host first to check if it's reachable
    ping -c 1 "$host" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Warning: Cannot ping $host. This might be expected in Docker networks."
    else
        echo "Host $host is reachable via ping."
    fi
    
    # Try to connect to the service
    while ! nc -z "$host" "$port" > /dev/null 2>&1; do
        retries=$((retries + 1))
        if [ $retries -eq $max_retries ]; then
            echo "Error: $service_name not ready after $max_retries retries"
            echo "Diagnostic information:"
            echo "- Trying to connect to: $host:$port"
            echo "- Current network configuration:"
            ip addr show
            echo "- DNS resolution:"
            getent hosts "$host" || echo "Cannot resolve $host"
            echo "- Testing connection with verbose output:"
            nc -zv "$host" "$port" || echo "Connection failed"
            exit 1
        fi
        echo "Attempt $retries/$max_retries: $service_name not ready yet..."
        sleep 2
    done
    echo "$service_name is ready at $host:$port!"
}

# Function to verify Python package installation
verify_package() {
    package_name="$1"
    echo "Verifying installation of $package_name..."
    if ! python -c "import $package_name" > /dev/null 2>&1; then
        echo "$package_name not found, installing..."
        pip install --no-cache-dir "$package_name"
        echo "$package_name installed successfully."
    else
        echo "$package_name is already installed."
    fi
}

# Wait for required services
echo "Waiting for PostgreSQL to be ready..."

# Install PostgreSQL client if not available
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL client not found, installing..."
    apt-get update && apt-get install -y postgresql-client
fi

# Try to connect to PostgreSQL directly using psql
max_retries=60
retries=0
while ! PGPASSWORD=postgres psql -h db -U postgres -d propos4l -c "SELECT 1;" > /dev/null 2>&1; do
    retries=$((retries + 1))
    if [ $retries -eq $max_retries ]; then
        echo "Error: PostgreSQL not ready after $max_retries retries"
        echo "Diagnostic information:"
        echo "- Testing connection with psql:"
        PGPASSWORD=postgres psql -h db -U postgres -d propos4l -c "SELECT 1;" || echo "Connection failed"
        echo "- Testing connection with nc:"
        nc -zv db 5432 || echo "Connection failed"
        echo "- DNS resolution:"
        getent hosts db || echo "Cannot resolve db"
        echo "- Network interfaces:"
        ip addr show
        exit 1
    fi
    echo "Attempt $retries/$max_retries: PostgreSQL not ready yet..."
    sleep 2
done
echo "PostgreSQL is ready!"

# Wait for Redis
echo "Waiting for Redis to be ready..."

# Install Redis client if not available
if ! command -v redis-cli &> /dev/null; then
    echo "Redis client not found, installing..."
    apt-get update && apt-get install -y redis-tools
fi

# Try to connect to Redis directly using redis-cli
max_retries=60
retries=0
while ! redis-cli -h redis ping > /dev/null 2>&1; do
    retries=$((retries + 1))
    if [ $retries -eq $max_retries ]; then
        echo "Error: Redis not ready after $max_retries retries"
        echo "Diagnostic information:"
        echo "- Testing connection with redis-cli:"
        redis-cli -h redis ping || echo "Connection failed"
        echo "- Testing connection with nc:"
        nc -zv redis 6379 || echo "Connection failed"
        echo "- DNS resolution:"
        getent hosts redis || echo "Cannot resolve redis"
        echo "- Network interfaces:"
        ip addr show
        exit 1
    fi
    echo "Attempt $retries/$max_retries: Redis not ready yet..."
    sleep 2
done
echo "Redis is ready!"

# Create required directories if they don't exist
mkdir -p /app/storage/pdfs /app/storage/templates /app/data

# Verify critical dependencies
echo "Verifying critical dependencies..."
verify_package "sqlmodel"
verify_package "pdf2image"
verify_package "faiss_cpu"
verify_package "keybert"
verify_package "yake"
verify_package "spacy"
verify_package "langchain_community"

# Verify spaCy models
echo "Verifying spaCy models..."
if ! python -c "import spacy; spacy.load('en_core_web_lg')" > /dev/null 2>&1; then
    echo "spaCy model en_core_web_lg not found, downloading..."
    python -m spacy download en_core_web_lg
    echo "spaCy model en_core_web_lg downloaded successfully."
else
    echo "spaCy model en_core_web_lg is already installed."
fi

# Set Python path
export PYTHONPATH=/app:$PYTHONPATH

# Handle different commands
case "$1" in
    "migrate")
        echo "Running database migrations..."
        alembic upgrade head
        ;;
    "debug")
        echo "Starting server in debug mode..."
        python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --reload \
            --log-level ${LOG_LEVEL:-info}
        ;;
    "serve")
        echo "Starting server in normal mode..."
        uvicorn app.main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --reload \
            --log-level ${LOG_LEVEL:-info}
        ;;
    *)
        echo "Unknown command: $1"
        echo "Available commands: migrate, debug, serve"
        exit 1
        ;;
esac
