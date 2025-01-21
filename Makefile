# Makefile for CryptoCurrency Portfolio Tracker

# Variables
VENV_NAME := venv
PYTHON := python3
PIP := pip3
APP_PATH := src/app.py
REQUIREMENTS := requirements.txt
TEST_PATH := tests/test_clients.py

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

.PHONY: all venv install run test clean help

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
	@. $(ACTIVATE) && $(PYTHON_VENV) $(APP_PATH)

# Run unit tests
test: venv
	@echo "Running unit tests..."
	@. $(ACTIVATE) && $(PYTHON_VENV) -m unittest $(TEST_PATH)

# Clean up virtual environment
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_NAME)
	@echo "Cleanup complete!"

# Help target
help:
	@echo "Available targets:"
	@echo "  make          : Sets up venv, installs requirements, and runs the app"
	@echo "  make venv     : Creates virtual environment if it doesn't exist"
	@echo "  make install  : Installs requirements in virtual environment"
	@echo "  make run      : Runs the application"
	@echo "  make test     : Runs unit tests"
	@echo "  make clean    : Removes virtual environment"
	@echo "  make help     : Shows this help message"
