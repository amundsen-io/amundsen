ARG METADATASERVICE_BASE
ARG SEARCHSERVICE_BASE

FROM node:8-slim as node-stage
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

COPY requirements3.txt /app/requirements3.txt
RUN pip3 install -r requirements3.txt

COPY --from=node-stage /app /app

RUN python3 setup.py install

ENTRYPOINT [ "python3" ]
CMD [ "amundsen_application/wsgi.py" ]
