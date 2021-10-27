#!/bin/bash -ex
# az acr login --name gblacriguazunonprod001
docker build -f ./Dockerfile.frontend.public -t amundsen-front-ztech-public .
docker tag amundsen-front-ztech-public  gblacriguazunonprod001.azurecr.io/new-amundsen/amundsen-front-ztech-public:1.1.4
docker push gblacriguazunonprod001.azurecr.io/new-amundsen/amundsen-front-ztech-public:1.1.4

docker build -f ./Dockerfile.search.public -t amundsen-search-ztech .
docker tag amundsen-search-ztech  gblacriguazunonprod001.azurecr.io/new-amundsen/amundsen-search-ztech:1.1.4
docker push gblacriguazunonprod001.azurecr.io/new-amundsen/amundsen-search-ztech:1.1.4

docker build -f ./Dockerfile.metadata.public -t amundsen-metadata-ztech .
docker tag amundsen-metadata-ztech  gblacriguazunonprod001.azurecr.io/new-amundsen/amundsen-metadata-ztech:1.1.4
docker push gblacriguazunonprod001.azurecr.io/new-amundsen/amundsen-metadata-ztech:1.1.4
