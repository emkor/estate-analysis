all: clean venv install

PY3 = python
VENV = .venv/estate-analysis
VENV_PY3 = $(VENV)/bin/python

clean:
	@echo "---- Cleaning cache and temporary files ----"
	@rm -rf $(VENV)

venv:
	@echo "---- Installing virtualenv ----"
	@mkdir -p $(VENV)
	@$(PY3) -m venv $(VENV)
	@$(PY3) -m pip install --upgrade pip

install:
	@$(VENV_PY3) -m pip install -r requirements.txt

.PHONY: all clean venv install
