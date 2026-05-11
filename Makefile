PYTHON_SYS = python3
PIP = $(VENV)/bin/pip
VENV = venv
PYTHON_VENV = $(VENV)/bin/python
MAIN = fly_in.py

FLAGS ?=
FILE ?=
ARGS ?=

$(VENV)/bin/activate: requirements.txt
	$(PYTHON_SYS) -m venv $(VENV)
	$(PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate

venv: $(VENV)/bin/activate

install: venv

gen_map: venv
	@echo "Creating temporary test map..."
	@echo "nb_drones: 4" > tmp_map.txt
	@echo "start_hub: start 0 0 [zone=normal color=green max_drones=4]" >> tmp_map.txt
	@echo "hub: block 2 -1 [zone=blocked color=red max_drones=1]" >> tmp_map.txt
	@echo "hub: prio 2 1 [zone=priority color=cyan max_drones=2]" >> tmp_map.txt
	@echo "hub: restr 4 1 [zone=restricted color=purple max_drones=1]" >> tmp_map.txt
	@echo "hub: norm 4 -1 [zone=normal color=blue max_drones=3]" >> tmp_map.txt
	@echo "end_hub: goal 6 0 [zone=normal color=gold max_drones=4]" >> tmp_map.txt
	@echo "connection: start-prio [max_link_capacity=2]" >> tmp_map.txt
	@echo "connection: start-block [max_link_capacity=1]" >> tmp_map.txt
	@echo "connection: prio-restr [max_link_capacity=1]" >> tmp_map.txt
	@echo "connection: block-norm [max_link_capacity=1]" >> tmp_map.txt
	@echo "connection: restr-goal [max_link_capacity=2]" >> tmp_map.txt
	@echo "connection: norm-goal [max_link_capacity=3]" >> tmp_map.txt
	@echo "connection: prio-norm [max_link_capacity=1]" >> tmp_map.txt
	$(PYTHON_VENV) $(DEBUG_FLAG) $(MAIN) tmp_map.txt $(ARGS)

run: venv
ifeq ($(strip $(FILE)),)
	@$(MAKE) gen_map
else
	$(PYTHON_VENV) $(MAIN) $(FILE) $(ARGS)
endif

debug: venv
	@echo "Running debug mode..."
ifeq ($(strip $(FILE)),)
	@$(MAKE) gen_map DEBUG_FLAG="-m pdb"
else
	$(PYTHON_VENV) -m pdb $(MAIN) $(FILE) $(ARGS)
endif

clean:
	@echo "Cleaning..."
	rm -rf $(VENV)
	find . -name "__pycache__" -exec rm -rf {} + 
	find . -name "*.pyc" -exec rm -rf {} + 
	rm -rf tmp_map.txt
	@echo "done!"

lint: venv
	@echo "flake8 + mypy checks..."
	$(PYTHON_VENV) -m flake8 . --exclude=$(VENV),build,dist
	$(PYTHON_VENV) -m mypy . --exclude $(VENV) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@echo "done!"

lint-strict: venv
	@echo "flake8 + STRICT mypy checks..."
	$(PYTHON_VENV) -m flake8 . --exclude=$(VENV),build,dist
	$(PYTHON_VENV) -m mypy . --exclude $(VENV) --strict
	@echo "done!"