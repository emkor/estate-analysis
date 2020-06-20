setup: clean venv install
all: dl-data analyze render

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

analyze:
	@echo "---- Analyzing data ----"
	@$(PY3) src/cache_places.py "data/place_cache.csv" $$MAPQUEST_API_KEY "offers"
	@rm -f "data/offers.db"
	@$(PY3) src/import_into_db.py "data/offers.db" "src/ddl.sql" "data/place_cache.csv" "offers"
	@$(PY3) src/dump_views.py "data/offers.db" "data"

render:
	@echo "---- Rendering data ----"
	@$(PY3) src/city_avg_geojson.py "data/avg_city_price.csv" "data/avg_city_prices.json"
	@$(PY3) src/render_map.py "data/isochrone_wroclaw_car_56min_7min.json" "map/map.json" "data/train_station.json" "data/avg_city_prices.json"

.PHONY: setup clean venv install all dl-data analyze render
