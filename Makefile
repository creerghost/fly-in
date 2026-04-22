PYTHON_SYS = python3
PIP = $(VENV)/bin/pip
VENV = venv
PYTHON_VENV = $(VENV)/bin/python
MAIN = fly_in.py

$(VENV)/bin/activate: requirements.txt
	$(PYTHON_SYS) -m venv $(VENV)
	$(PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate

venv: $(VENV)/bin/activate

install: venv

run: venv
	$(PYTHON_VENV) $(MAIN)

clean:
	find . -name "__pycache__" -exec rm -rf {} + 
	find . -name "*.pyc" -exec rm -rf {} + 

lint: venv
	$(PYTHON_VENV) -m flake8 . --exclude=$(VENV),build,dist
	$(PYTHON_VENV) -m mypy . --exclude $(VENV) --ignore-missing-imports --disallow-untyped-defs

lint-strict: venv
	$(PYTHON_VENV) -m flake8 . --exclude=$(VENV),build,dist
	$(PYTHON_VENV) -m mypy . --exclude $(VENV) --strict