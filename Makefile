.PHONY: help test run clean

help:
	@echo "Available commands:"
	@echo "  make test   Run the complete test suite"
	@echo "  make run    Launch ABC DIGITAL Bill Generator (bill_generator.py)"
	@echo "  make clean  Clean compiled bytecode and temporary artifacts"

test:
	python3 -m unittest discover tests -v

run:
	python3 bill_generator.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
