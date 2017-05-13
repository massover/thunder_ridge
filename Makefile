develop:
	pip install requirements-dev.txt

deploy:
	lambda deploy

lint:
	flake8

test:
	py.test tests.py