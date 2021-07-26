FROM python:3.7-slim as base
WORKDIR /app
RUN pip3 install gunicorn

RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install git -y

COPY ./metadata/ /app
COPY requirements-dev.txt /app/requirements-dev.txt
COPY requirements-common.txt /app/requirements-common.txt

CMD [ "python3", "metadata_service/metadata_wsgi.py" ]

FROM base as oidc-release

RUN  pip3 install -e .&& \
     pip3 install -e .[oidc]

ENV FLASK_APP_MODULE_NAME flaskoidc
ENV FLASK_APP_CLASS_NAME FlaskOIDC
ENV FLASK_OIDC_WHITELISTED_ENDPOINTS status,healthcheck,health
ENV SQLALCHEMY_DATABASE_URI sqlite:///sessions.db

# You will need to set these environment variables in order to use the oidc image
# FLASK_OIDC_CONFIG_URL - url endpoint for your oidc provider config
# FLASK_OIDC_PROVIDER_NAME - oidc provider name
# FLASK_OIDC_CLIENT_ID - oidc client id
# FLASK_OIDC_CLIENT_SECRET - oidc client secret

FROM base as release
RUN pip3 install -e .
