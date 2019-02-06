clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

test_unit:
	python3 -bb -m pytest tests

lint:
	flake8 .

test: test_unit lint
