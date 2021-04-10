ARG METADATASERVICE_BASE
ARG SEARCHSERVICE_BASE

FROM node:12-slim as node-stage
WORKDIR /app/amundsen_application/static

COPY amundsen_application/static/package.json /app/amundsen_application/static/package.json
COPY amundsen_application/static/package-lock.json /app/amundsen_application/static/package-lock.json
RUN npm install

COPY amundsen_application/static/ /app/amundsen_application/static/
RUN npm rebuild node-sass
RUN npm run dev-build

COPY . /app

FROM python:3.7-slim
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY --from=node-stage /app /app

RUN pip3 install -e .

ENTRYPOINT [ "python3" ]
CMD [ "amundsen_application/wsgi.py" ]
