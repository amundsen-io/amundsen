clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

.PHONY: test_unit
test_unit: test_unit2_or3_if_its_default

lint:
	flake8 .

.PHONY: test
test: test_unit lint

.PHONY: test_unit
test_unit2_or3_if_its_default:
	python -bb -m pytest tests/unit

test_unit3:
	python3 -bb -m pytest tests/unit
