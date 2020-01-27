
build-frontend:
	cd amundsenfrontendlibrary && make image
build-metadata:
	cd amundsenmetadatalibrary && make image
build-amundsen:
	docker-compose -f docker-amundsen.yml up -d
build-all: build-frontend build-metadata build-amundsen