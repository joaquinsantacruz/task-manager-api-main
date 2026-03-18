#!/bin/bash
# Run Tests Script
# Usage:
#   ./run-tests.sh setup        - Setup test database only
#   ./run-tests.sh setup-test   - Setup and run all tests
#   ./run-tests.sh test         - Run tests only (default)
#   ./run-tests.sh              - Run tests only (default)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ACTION="${1:-test}"

# Detect available test runner (priority: uv > .venv > venv > python3)
if command -v uv &> /dev/null; then
    RUNNER="uv run pytest"
elif [ -f ".venv/bin/python" ]; then
    RUNNER=".venv/bin/python -m pytest"
elif [ -f "venv/bin/python" ]; then
    RUNNER="venv/bin/python -m pytest"
elif command -v python3 &> /dev/null; then
    RUNNER="python3 -m pytest"
else
    echo "❌ Error: No Python environment found!"
    echo "  Run './setup-dev.sh' first to set up the environment."
    exit 1
fi

setup_test_database() {
    echo "🔧 Setting up test database..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Error: Docker is not running!"
        echo "  Please start Docker and run this script again."
        exit 1
    fi
    
    # Create test database
    echo "  Creating database 'taskmanager_test'..."
    docker exec taskmanager_db psql -U taskuser -d postgres -c "CREATE DATABASE taskmanager_test;" 2>/dev/null || true
    
    # Grant permissions
    echo "  Granting permissions..."
    docker exec taskmanager_db psql -U taskuser -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE taskmanager_test TO taskuser;"
    
    echo "✅ Test database setup complete!"
}

run_tests() {
    echo "🧪 Running tests..."
    echo "  Using: $RUNNER"
    
    # Run pytest with coverage
    $RUNNER --cov=src --cov-report=term --tb=short
    
    if [ $? -eq 0 ]; then
        echo "✅ All tests passed!"
    else
        echo "❌ Tests failed!"
        exit 1
    fi
}

# Main
case "$ACTION" in
    setup)
        setup_test_database
        ;;
    setup-test)
        setup_test_database
        echo ""
        run_tests
        ;;
    test)
        run_tests
        ;;
    *)
        echo "Usage: $0 [setup|setup-test|test]"
        echo "  setup       - Setup test database only"
        echo "  setup-test  - Setup and run all tests"
        echo "  test        - Run tests only (default)"
        exit 1
        ;;
esac
