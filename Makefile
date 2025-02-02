# Project settings
APP_NAME=app.py
VENV_DIR=venv
REQ_FILE=requirements.txt
DOCKER_COMPOSE_FILE=docker-compose.yml

.PHONY: all run setup clean docker-build docker-up docker-down lint

# Default target
all: run

# Run the application
run:
	@echo "Running the Streamlit application..."
	$(STREAMLIT_CMD) $(APP_NAME)

# Set up virtual environment and install requirements
setup:
	@echo "Setting up the project..."
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r $(REQ_FILE)

# Clean up unwanted files
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete

# Build Docker images
docker-build:
	@echo "Building Docker images..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) build

# Start Docker services
docker-up:
	@echo "Starting Docker containers..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d

# Stop Docker services
docker-down:
	@echo "Stopping Docker containers..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# Lint the project using streamlit
lint:
	@echo "Linting code..."
	stremlit run app.py
