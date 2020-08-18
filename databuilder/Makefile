clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

.PHONY: test_unit
test_unit:
	python3 -bb -m pytest tests

lint:
	flake8 .

.PHONY: mypy
mypy:
	mypy .

.PHONY: test
test: test_unit lint mypy

