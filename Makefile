.PHONY: run install test clean

# Default target
all: install

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	python run.py

# Run tests
test:
	pytest tests/

# Clean build artifacts
clean:
	rm -rf __pycache__/ build/ dist/ *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install in development mode
dev-install:
	pip install -e .

# Install development dependencies
dev-setup: dev-install
	pip install pytest pytest-cov black flake8

# Format code
format:
	black app/ tests/

# Check code style
lint:
	flake8 app/ tests/
