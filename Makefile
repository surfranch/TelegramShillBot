.PHONY: help clean setup format lint test flt run

.DEFAULT: help

help:
	@echo "make clean			deactivate and remove venv and any leftover *.session files"
	@echo "make setup			create venv and pip install requirements.txt"
	@echo "make format			run black"
	@echo "make lint			run pylint"
	@echo "make test			run unittest"
	@echo "make flt			run make format, make lint, and make test"
	@echo "make run			run the bot"

clean:
	@deactivate > /dev/null 2>&1 || echo "skipping deactivate"
	@rm -fr venv *.session

setup:
	@python3 -m venv venv
	@. venv/bin/activate && pip install -r requirements.txt

format:
	@. venv/bin/activate && black *.py

lint:
	@. venv/bin/activate && pylint tg_shill_bot.py

test:
	@. venv/bin/activate && python test_tg_shill_bot.py

flt: format lint test

run:
	@. venv/bin/activate && python tg_shill_bot.py
