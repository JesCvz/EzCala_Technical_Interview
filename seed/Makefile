.PHONY: setup seed run test
setup:
	pip install -r requirements.txt
seed:
	python -m app.seed_data
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
test:
	pytest -v
