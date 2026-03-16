install:
	pip install -r requirements.txt && cd frontend && npm install

dev-backend:
	python manage.py runserver

dev-frontend:
	cd frontend && npm run dev

migrate:
	python manage.py migrate

setup:
	python manage.py migrate && python manage.py collectstatic --noinput

build-frontend:
	cd frontend && npm run build

shell:
	python manage.py shell

createsuperuser:
	python manage.py createsuperuser

seo-check:
	python scripts/seo_check.py

seo-check-issues:
	python scripts/seo_check.py --issues-only

lighthouse:
	npx @lhci/cli@0.13.x autorun

.PHONY: install dev-backend dev-frontend migrate setup build-frontend shell createsuperuser seo-check seo-check-issues lighthouse
