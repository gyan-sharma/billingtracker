#!/bin/bash

# Configuration
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
UPLOADS_DIR="$BACKEND_DIR/uploads"
OUTPUTS_DIR="$BACKEND_DIR/outputs"
VENV_DIR="$PROJECT_ROOT/venv"
BACKEND_PORT=5002
FRONTEND_PORT=8002

# Helper Functions
check_dependency() {
    if ! command -v "$1" &>/dev/null; then
        echo "Error: $1 is not installed. Please install it and rerun the script."
        exit 1
    fi
}

check_directory() {
    if [ ! -d "$1" ]; then
        echo "Directory $1 does not exist. Creating it..."
        mkdir -p "$1"
    fi
}

kill_process_on_port() {
    PORT=$1
    if lsof -ti:$PORT &>/dev/null; then
        echo "Killing processes on port $PORT..."
        lsof -ti:$PORT | xargs kill -9
    else
        echo "No process running on port $PORT."
    fi
}

start_server() {
    local type=$1
    local dir=$2
    local port=$3
    local command=$4
    local log_file=$5
    local pid_file=$6

    echo "Starting $type server on port $port..."
    cd "$dir" || { echo "Error: $type directory not found."; exit 1; }
    nohup $command > "$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"
    echo "$type server started with PID $pid."
}

# Step 1: Check Dependencies
echo "Checking dependencies..."
check_dependency python3
check_dependency pip

# Step 2: Ensure Project Structure
echo "Creating and verifying project structure..."
check_directory "$BACKEND_DIR"
check_directory "$FRONTEND_DIR"
check_directory "$UPLOADS_DIR"
check_directory "$OUTPUTS_DIR"

# Step 3: Setup Python Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists. Skipping setup."
fi

# Step 4: Activate Virtual Environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate" || { echo "Failed to activate virtual environment."; exit 1; }

# Step 5: Check Pip Version (Skip Upgrade)
PIP_VERSION=$(pip --version | awk '{print $2}')
echo "pip is available (version: $PIP_VERSION)."

# Check for latest version (fallback to current version if check fails)
LATEST_PIP_VERSION=$(pip search pip 2>/dev/null | sed -n 's/.*pip (\([^)]*\)).*/\1/p' | head -n1 || echo "$PIP_VERSION")
if [ "$LATEST_PIP_VERSION" != "$PIP_VERSION" ]; then
    echo "Note: A newer version of pip ($LATEST_PIP_VERSION) is available. You may consider upgrading it later."
fi

# Step 6: Install Required Python Packages
echo "Installing required Python packages..."
pip install flask flask-cors pandas openpyxl xlsxwriter >/dev/null || { echo "Dependency installation failed."; exit 1; }

# Step 7: Kill Existing Processes on Ports and Start Backend and Frontend
kill_process_on_port $BACKEND_PORT
kill_process_on_port $FRONTEND_PORT

echo "Starting backend server on port $BACKEND_PORT..."
cd "$BACKEND_DIR"
nohup python3 process.py > "$PROJECT_ROOT/backend.log" 2>&1 &

echo "Starting frontend server on port $FRONTEND_PORT..."
cd "$FRONTEND_DIR"
nohup python3 -m http.server $FRONTEND_PORT > "$PROJECT_ROOT/frontend.log" 2>&1 &

echo "Setup complete!"
echo "Backend is running on: http://127.0.0.1:$BACKEND_PORT"
echo "Frontend is running on: http://127.0.0.1:$FRONTEND_PORT"


# Final Message
echo "Setup complete. Use CTRL+C to stop the servers."
