develop:
	pip install requirements-dev.txt

deploy:
	lambda deploy

test:
	py.test tests.py