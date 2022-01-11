#!/bin/bash -ex
# az acr login --name gblacriguazuprod001
docker build -f ./Dockerfile.frontend.public -t front-public .
docker tag front-public  gblacriguazuprod001.azurecr.io/pharos/front-public:1.0.9
docker push gblacriguazuprod001.azurecr.io/pharos/front-public:1.0.9

docker build -f ./Dockerfile.search.public -t search .
docker tag search  gblacriguazuprod001.azurecr.io/pharos/search:1.0.9
docker push gblacriguazuprod001.azurecr.io/pharos/search:1.0.9

docker build -f ./Dockerfile.metadata.public -t metadata .
docker tag metadata  gblacriguazuprod001.azurecr.io/pharos/metadata:1.0.9
docker push gblacriguazuprod001.azurecr.io/pharos/metadata:1.0.9
