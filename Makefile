# link mode was set to copy to eliminate cross-filesystem cache warnings
export UV_LINK_MODE ?= copy

RESET   = \033[0m
BOLD    = \033[1m
RED     = \033[1;31m
GREEN   = \033[1;32m
YELLOW  = \033[1;33m
BLUE    = \033[1;34m
MAGENTA = \033[1;35m
CYAN    = \033[1;36m

# --active -> uv uses your active environment cleanly without warnings
# --group dev -> include dev developments so tools like mypy are always resolved in the env
UV      = uv
PYTHON  = $(UV) run --group dev --active python

FILE    ?= $(file)
ARGS    ?= --renderer pygame

.PHONY: install gen_map run debug clean lint lint-strict lint-fix help


install:
	@printf "$(CYAN)Syncing dependencies with uv...$(RESET)\n"
	$(UV) sync

gen_map:
	@printf "Creating temporary test map...\n"
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
	$(PYTHON) $(DEBUG_FLAG) -m src tmp_map.txt $(ARGS)

run:
ifeq ($(strip $(FILE)),)
	@printf "$(YELLOW)FILE argument was not provided. Running default map...\n$(RESET)"
	@$(MAKE) gen_map; status=$$?; $(MAKE) clean-cache; exit $$status
else
	$(PYTHON) -m src $(FILE) $(ARGS); status=$$?; $(MAKE) clean-cache; exit $$status
endif

debug:
	@printf "$(YELLOW)Running debug mode...\n$(RESET)"
ifeq ($(strip $(FILE)),)
	@$(MAKE) gen_map DEBUG_FLAG="-m pdb"
else
	$(PYTHON) -m pdb -m src $(FILE) $(ARGS)
endif


clean:
	@printf "$(YELLOW)Cleaning caches, temporary files and venv...\n$(RESET)"
	rm -rf .venv venv
	rm -rf .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
	rm -f tmp_map.txt
	@printf "$(GREEN)Done!$(RESET)\n"

clean-cache:
	@printf "$(YELLOW)Cleaning caches and temporary files...\n$(RESET)"
	rm -rf .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
	rm -f tmp_map.txt
	@printf "$(GREEN)Done!$(RESET)\n"

lint:
	@printf "$(YELLOW)Running flake8 and mypy checks...\n$(RESET)"
	$(PYTHON) -m flake8 . --exclude=".venv/,scripts/"
	$(PYTHON) -m mypy . --exclude="(\.venv|scripts)" --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@printf "$(GREEN)Done!$(RESET)\n"

lint-strict:
	@printf "$(YELLOW)Running flake8 and STRICT mypy checks...\n$(RESET)"
	$(PYTHON) -m flake8 . --exclude=".venv/,scripts/"
	$(PYTHON) -m mypy . --exclude="(\.venv|scripts)" --strict
	@printf "$(GREEN)Done!$(RESET)\n"

lint-fix:
	@printf "$(YELLOW)Automatically fixing lint and format errors...\n$(RESET)"
	$(PYTHON) -m ruff check --select E,W,F,I --fix --line-length 79 . || true
	$(PYTHON) -m ruff format --line-length 79 .
	@printf "$(GREEN)Done!$(RESET)\n"


help:
	@printf "============================================================================\n"
	@printf "Welcome to the Makefile for the project!\n"
	@printf "This project has been created as a part of 42 curriculum by $(RED)vlnikola$(RESET).\n"
	@printf "$(RED)Ensure you have $(BOLD)$(GREEN)uv$(RED) installed and available in your environment.$(RESET)\n"
	@printf "$(RESET)----------------------------------------------------------------------------$(RESET)\n"
	@printf "$(YELLOW)Available targets:$(RESET)\n"
	@printf "  $(GREEN)install$(RESET)            - Install dependencies using uv\n"
	@printf "  $(GREEN)run$(RESET)                - Run the main pipeline\n"
	@printf "  $(GREEN)debug$(RESET)              - Run the main script in debug mode using pdb\n"
	@printf "  $(GREEN)clean$(RESET)              - Remove temporary files and caches\n"
	@printf "  $(GREEN)lint$(RESET)               - Run code linting and type checking\n"
	@printf "  $(GREEN)lint-strict$(RESET)        - Run strict code linting and type checking\n"
	@printf "  $(GREEN)lint-fix$(RESET)           - Automatically fix formatting and lint errors\n"
	@printf "  $(GREEN)help$(RESET)               - Show this help message\n"

	@printf "$(YELLOW)Optional arguments:$(RESET)\n"
	@printf "  $(BLUE)FILE=path/to/map$(RESET)            - Specify a map file\n"
	@printf "  $(BLUE)ARGS='--renderer pygame --speed=2.0'$(RESET) - Specify additional arguments\n"
	@printf ""
	@printf "$(YELLOW)Examples:$(RESET)\n"
	@printf "  make $(GREEN)run$(RESET) $(BLUE)FILE=maps/challenge/01_the_impossible_dream.txt$(RESET)\n"
	@printf "  make $(GREEN)run$(RESET) $(BLUE)FILE=maps/challenge/01_the_impossible_dream.txt ARGS='--renderer pygame --speed=2.0'$(RESET)\n"
	@printf "============================================================================\n"