setup: clean venv install
all: dl-data analyze render

PY3 = python
VENV = .venv/estate-analysis
VENV_PY3 = $(VENV)/bin/python
VENV_B2 = $(VENV)/bin/b2
BUCKET_CACHE_DIR = "bucket"
DATA_DIR = "offers"

clean:
	@echo "---- Cleaning cache and temporary files ----"
	@rm -rf .pytest_cache offers.db gist_update.json

venv:
	@echo "---- Installing virtualenv ----"
	@rm -rf $(VENV)
	@mkdir -p $(VENV)
	@$(PY3) -m venv $(VENV)
	@$(VENV_PY3) -m pip install --upgrade pip setuptools wheel

install:
	@echo "---- Installing dependencies ----"
	@$(VENV_PY3) -m pip install -r requirements.txt

dl-data:
	@echo "---- Downloading data ----"
	@bash dl-data.sh $(VENV_B2) $(BUCKET_CACHE_DIR) $(DATA_DIR)
	@echo "Bucket cache:" && ls $(BUCKET_CACHE_DIR) | sort
	@echo "Data cache:" && ls $(DATA_DIR) | sort

analyze:
	@echo "---- Analyzing data ----"
	@$(VENV_PY3) src/cache_places.py "data/place_cache.csv" $$MAPQUEST_API_KEY "offers"
	@$(VENV_PY3) src/city_distance.py "data/isochrone_wroclaw_car_56min_7min.json" "data/place_cache.csv" "data/time_to_wroclaw.csv"
	@rm -f "data/offers.db"
	@$(VENV_PY3) src/import_into_db.py "data/offers.db" "src/ddl.sql" "data/place_cache.csv" "data/time_to_wroclaw.csv" "offers" "data/uke/current" "data/uke/popc"

render:
	@echo "---- Rendering data ----"
	@$(VENV_PY3) src/dump_views.py --headers "data/offers.db" "data"
	@$(VENV_PY3) src/city_avg_geojson.py "data/avg_city_price.csv" "data/avg_city_prices.json" --headers
	@$(VENV_PY3) src/render_new_offers.py "data/last_10days_offers.csv" "data/recent_offers.json" --headers
	@$(VENV_PY3) src/render_inet.py "data/city_broadband.csv" "data/city_broadband.json"
	@$(VENV_PY3) src/render_map.py "data/isochrone_wroclaw_car_56min_7min.json" "parcel-map.json" "data/city_broadband.json" "data/train_station.json" "data/mpk_stops.json" "data/avg_city_prices.json"
	@$(VENV_PY3) src/render_map.py "data/isochrone_wroclaw_car_56min_7min.json" "offer-map.json" "data/city_broadband.json" "data/train_station.json" "data/mpk_stops.json" "data/recent_offers.json"
	@$(VENV_PY3) src/render_avg_gist_update.py "avg_gist_update.json"
	@$(VENV_PY3) src/render_offer_gist_update.py "offer_gist_update.json"

publish:
	@echo "---- Publishing data ----"
	@curl -H 'Accept: application/vnd.github.v3+json' -H "Content-Type: application/json" -H "Authorization: token $$GH_API_KEY" -d "@avg_gist_update.json" -X 'PATCH' "https://api.github.com/gists/$$GH_AVG_GIST_ID"
	@curl -H 'Accept: application/vnd.github.v3+json' -H "Content-Type: application/json" -H "Authorization: token $$GH_API_KEY" -d "@offer_gist_update.json" -X 'PATCH' "https://api.github.com/gists/$$GH_OFFER_GIST_ID"

.PHONY: setup clean venv install all dl-data analyze render publish
