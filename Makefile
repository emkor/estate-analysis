all: clean venv install

PY3 = python
VENV = .venv/estate-analysis
VENV_PY3 = $(VENV)/bin/python
BUCKET_CACHE_DIR = "bucket"
DATA_DIR = "offers"

clean:
	@echo "---- Cleaning cache and temporary files ----"
	@rm -rf $(VENV) .pytest_cache offers.db

venv:
	@echo "---- Installing virtualenv ----"
	@mkdir -p $(VENV)
	@$(PY3) -m venv $(VENV)
	@$(PY3) -m pip install --upgrade pip

install:
	@echo "---- Installing dependencies ----"
	@$(VENV_PY3) -m pip install -r requirements.txt

dl-data:
	@echo "---- Downloading data ----"
	sh dl-data.sh $(BUCKET_CACHE_DIR) $(DATA_DIR)


.PHONY: all clean venv install
