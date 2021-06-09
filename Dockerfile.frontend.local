ARG METADATASERVICE_BASE
ARG SEARCHSERVICE_BASE

FROM node:12-slim as node-stage
WORKDIR /app/amundsen_application/static

COPY ./frontend/amundsen_application/static/package.json /app/amundsen_application/static/package.json
COPY ./frontend/amundsen_application/static/package-lock.json /app/amundsen_application/static/package-lock.json
RUN npm install

COPY ./frontend/amundsen_application/static/ /app/amundsen_application/static/
RUN npm rebuild node-sass
RUN npm run dev-build

COPY ./frontend /app

FROM python:3.7-slim
WORKDIR /app

COPY ./frontend /app
COPY requirements-dev.txt /app/requirements-dev.txt
COPY requirements-common.txt /app/requirements-common.txt

COPY --from=node-stage /app /app

RUN pip3 install -e .

ENTRYPOINT [ "python3" ]
CMD [ "amundsen_application/wsgi.py" ]
