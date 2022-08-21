service ?= amundsen-lastest-service
DATE := $(shell date +%y.%W)
GIT_COMMIT_HASH := $(shell git rev-parse --short HEAD)
BUILD_VERSION  := $(service)-$(DATE)-$(GIT_COMMIT_HASH)




upload-frontend-to-ecr:
	docker build -f Dockerfile.frontend -t amundsen-frontend .
	docker tag amundsen-frontend:latest 848569320300.dkr.ecr.eu-west-1.amazonaws.com/amundsen-frontend:${BUILD_VERSION}
	docker push 848569320300.dkr.ecr.eu-west-1.amazonaws.com/amundsen-frontend:${BUILD_VERSION}


deploy-stg-frontend: upload-frontend-to-ecr
	curl -sX POST \
    	-F token=8f48a5a20911bff22b9191e6688a32 \
    	-F "ref=master" \
    	-F "variables[IMAGE_TAG]=${BUILD_VERSION}" \
    	-F "variables[ACTION]=${action}" \
    	-F "variables[DEV]=false" \
    	-F "variables[STAGING]=false" \
    	-F "variables[PROD]=true" \
    	"https://gitlab.sre.red/api/v4/projects/858/trigger/pipeline"





upload-metadata-to-ecr:
	docker build -f Dockerfile.metadata -t amundsen_metadata .
	docker tag amundsen_metadata:latest 848569320300.dkr.ecr.eu-west-1.amazonaws.com/amundsen-metadata:${BUILD_VERSION}
	docker push 848569320300.dkr.ecr.eu-west-1.amazonaws.com/amundsen-metadata:${BUILD_VERSION}


deploy-stg-metadata: upload-metadata-to-ecr
	curl -sX POST \
    	-F token=e490b460fb4d46563a084e87ae650b \
    	-F "ref=master" \
    	-F "variables[IMAGE_TAG]=${BUILD_VERSION}" \
    	-F "variables[ACTION]=${action}" \
    	-F "variables[DEV]=false" \
    	-F "variables[STAGING]=false" \
    	-F "variables[PROD]=true" \
    	"https://gitlab.sre.red/api/v4/projects/859/trigger/pipeline"



upload-search-to-ecr:
	docker build -f Dockerfile.search -t amundsen_search .
	docker tag amundsen_search:latest 848569320300.dkr.ecr.eu-west-1.amazonaws.com/amundsen-search:${BUILD_VERSION}
	docker push 848569320300.dkr.ecr.eu-west-1.amazonaws.com/amundsen-search:${BUILD_VERSION}

deploy-stg-search: upload-search-to-ecr
	curl -sX POST \
    	-F token=3b9e0f153934fd07c36ccce68060d2 \
    	-F "ref=master" \
    	-F "variables[IMAGE_TAG]=${BUILD_VERSION}" \
    	-F "variables[ACTION]=${action}" \
    	-F "variables[DEV]=false" \
    	-F "variables[STAGING]=false" \
    	-F "variables[PROD]=true" \
    	"https://gitlab.sre.red/api/v4/projects/860/trigger/pipeline"
