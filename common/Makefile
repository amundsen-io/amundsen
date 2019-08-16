 clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

 test_unit:
	python -m pytest tests
	python3 -bb -m pytest tests

 test: test_unit
