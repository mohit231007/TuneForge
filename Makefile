.PHONY: install install-qlora lint test api studio web worker train evaluate compose

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

install-qlora:
	pip install -e ".[dev,qlora]"

lint:
	ruff check src tests app api

test:
	pytest -q

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

studio:
	streamlit run app/app.py

web:
	cd web && npm install && npm run dev

worker:
	python -m tuneforge.worker

train:
	python -m tuneforge.train --config configs/tinyllama_dolly.yaml

evaluate:
	@echo "Usage: python -m tuneforge.evaluate --config configs/tinyllama_dolly.yaml --adapter <adapter-path>"

compose:
	docker compose up --build
