IMAGE := amundsendev/amundsen-metadata
OIDC_IMAGE := ${IMAGE}-oidc
VERSION:= $(shell grep -m 1 '__version__' setup.py | cut -d '=' -f 2 | tr -d "'" | tr -d '[:space:]')

.PHONY: clean
clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

.PHONY: test_unit
test_unit:
	python3 -b -m pytest tests

lint:
	python3 -m flake8

.PHONY: mypy
mypy:
	mypy --ignore-missing-imports --follow-imports=skip --strict-optional --warn-no-return .

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

.PHONY: oidc-image
oidc-image:
	docker build -f public.Dockerfile --target=oidc-release -t ${OIDC_IMAGE}:${VERSION} .
	docker tag ${OIDC_IMAGE}:${VERSION} ${OIDC_IMAGE}:latest

.PHONY: push-odic-image
push-oidc-image:
	docker push ${OIDC_IMAGE}:${VERSION}
	docker push ${OIDC_IMAGE}:latest

.PHONY: build-push-image
build-push-image: image oidc-image push-image push-oidc-image
