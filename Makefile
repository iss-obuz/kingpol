.PHONY: help init clean clean-build clean-misc lint mypy test cov-run cov-report coverage list-deps build

help:
	@echo "init - initialize environment and version control"
	@echo "clean - clean non-persistent files"
	@echo "clean-build - remove build artifacts"
	@echo "clean-misc - remove various Python file artifacts"

init:
	git init
	pip install -e .[dev]
	pre-commit install
	mkdir -p data/raw
	mkdir -p data/proc
	mkdir -p data/remote
	mkdir -p scripts
	dvc init --force
	dvc remote add  --default kingpol ${PWD}/data/remote --local --force
	dvc config core.autostage true

clean: clean-build clean-misc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-misc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '.benchmarks' -exec rm -rf {} +
	find . -name '.pytest-cache' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.ruff_cache' -exec rm -rf {} +
