# Makefile for CryptoCurrency Portfolio Tracker

# Variables
VENV_NAME := venv
PYTHON := python3
PIP := pip3
APP_PATH := src/app.py
REQUIREMENTS := requirements.txt
CREDENTIALS_DIR := src/credentials
CREDENTIALS_FILE := $(CREDENTIALS_DIR)/credentials.json

# Check if we're on Windows
ifeq ($(OS),Windows_NT)
	PYTHON_VENV := $(VENV_NAME)/Scripts/python
	PIP_VENV := $(VENV_NAME)/Scripts/pip
	ACTIVATE := $(VENV_NAME)/Scripts/activate
else
	PYTHON_VENV := $(VENV_NAME)/bin/python
	PIP_VENV := $(VENV_NAME)/bin/pip
	ACTIVATE := $(VENV_NAME)/bin/activate
endif

.PHONY: all venv install run clean credentials

# Default target
all: venv install run

# Create virtual environment if it doesn't exist
venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_NAME); \
	else \
		echo "Virtual environment already exists."; \
	fi

# Install requirements
install: venv
	@echo "Installing requirements..."
	@. $(ACTIVATE) && $(PIP_VENV) install -r $(REQUIREMENTS)

# Run the application
run: venv
	@echo "Running application..."
	@cd src && . ../$(ACTIVATE) && $(PYTHON) app.py

# Clean up virtual environment
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_NAME)
	@echo "Cleanup complete!"

# Create credentials directory and template file if they don't exist
credentials:
	@if [ ! -d "$(CREDENTIALS_DIR)" ]; then \
		echo "Creating credentials directory..."; \
		mkdir -p $(CREDENTIALS_DIR); \
	fi
	@if [ ! -f "$(CREDENTIALS_FILE)" ]; then \
		echo "Creating template credentials.json..."; \
		echo '{\n    "api_key": "your_api_key_here",\n    "api_secret": "your_api_secret_here"\n}' > $(CREDENTIALS_FILE); \
		echo "Please update $(CREDENTIALS_FILE) with your actual credentials."; \
	fi

# Help target
help:
	@echo "Available targets:"
	@echo "  make          : Sets up venv, installs requirements, and runs the app"
	@echo "  make venv     : Creates virtual environment if it doesn't exist"
	@echo "  make install  : Installs requirements in virtual environment"
	@echo "  make run      : Runs the application"
	@echo "  make clean    : Removes virtual environment"
	@echo "  make credentials: Creates credentials directory and template file"
	@echo "  make help     : Shows this help message"