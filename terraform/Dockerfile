FROM hashicorp/terraform:0.14.3

RUN apk update && apk add bash gettext nodejs npm zip

RUN mkdir -p /app/terraform
WORKDIR /app/terraform

COPY . /app/terraform
RUN chmod a+x entrypoint.sh

ENV TF_INPUT=0
ENV TF_IN_AUTOMATION=1
RUN cd main/config && terraform init

ENTRYPOINT ["./entrypoint.sh"]
