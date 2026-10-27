.PHONY: install run migrate createsuperuser shell test coverage clean docker-build docker-up docker-down

# Install dependencies
install:
	pip install -r requirements.txt

# Run Django development server
run:
	python manage.py runserver

# Run with custom port
run-dev:
	python manage.py runserver 0.0.0.0:8000

# Database migrations
migrate:
	python manage.py migrate

# Create superuser
createsuperuser:
	python manage.py createsuperuser

# Django shell
shell:
	python manage.py shell

# Run tests
test:
	python manage.py test

# Coverage
coverage:
	python manage.py test --coverage

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +

# Docker build
docker-build:
	docker-compose build

# Docker up
docker-up:
	docker-compose up -d

# Docker down
docker-down:
	docker-compose down

# Docker logs
docker-logs:
	docker-compose logs -f
