#!/bin/bash

set -x
set -e
set -o pipefail

touch /var/tmp/gatewayapi_post_new.zip # This is an annoying hack; terraform requires the zip files exists

cd main/config

for file in *.envsubst; do \
  envsubst < ${file} > ${file%.envsubst}; \
done

export TF_INPUT=0
export TF_IN_AUTOMATION=1
export TF_CLI_ARGS="-no-color"

terraform init
exec env TF_VAR_env_id=${RELEASE_ENV_ID} TF_VAR_backend_ingress_url=${BACKEND_INGRESS_URL} terraform $@
