.PHONY: dev api frontend install test

dev:
	@echo "Starting API on :8000 and frontend on :4782..."
	@trap 'kill 0' INT TERM; \
	(cd $(CURDIR) && . venv/bin/activate && uvicorn api:app --reload) & \
	(cd $(CURDIR)/frontend && npm run dev) & \
	wait

api:
	. venv/bin/activate && uvicorn api:app --reload

frontend:
	cd frontend && npm run dev

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

test:
	. venv/bin/activate && pytest -v
