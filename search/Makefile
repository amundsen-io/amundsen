IMAGE := amundsendev/amundsen-search
VERSION:= $(shell grep -m 1 '__version__' setup.py | cut -d '=' -f 2 | tr -d "'" | tr -d '[:space:]')

.PHONY: test
clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

.PHONY: test_unit
test_unit:
	python3 -bb -m pytest tests

.PHONY: lint
lint:
	flake8 .

.PHONY: mypy
mypy:
	mypy --ignore-missing-imports --strict-optional --warn-no-return .

.PHONY: test
test: test_unit lint mypy

.PHONY: image
image:
	docker build -f public.Dockerfile -t ${IMAGE}:${VERSION} .
	docker tag ${IMAGE}:${VERSION} ${IMAGE}:latest

.PHONY: push-image
push-image:
	docker push ${IMAGE}:${VERSION}
	docker push ${IMAGE}:latest

.PHONY: build-push-image
build-push-image: image push-image
