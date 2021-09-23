.PHONY: help clean setup format lint run

.DEFAULT: help

help:
	@echo "make clean"
	@echo "make setup"
	@echo "make format"
	@echo "make lint"
	@echo "make run"

clean:
	@deactivate > /dev/null 2>&1 || echo "skipping deactivate"
	@rm -fr venv *.session

setup:
	@python3 -m venv venv
	@. venv/bin/activate && pip install -r requirements.txt

format:
	@. venv/bin/activate && black *.py

lint:
	@. venv/bin/activate && pylint *.py

run:
	@. venv/bin/activate && python tg_shill_bot.py
