FROM node:8-slim as node-stage
WORKDIR /app/amundsen_application/static

COPY amundsen_application/static/package.json /app/amundsen_application/static/package.json
COPY amundsen_application/static/package-lock.json /app/amundsen_application/static/package-lock.json
RUN npm install

COPY amundsen_application/static /app/amundsen_application/static
RUN npm run build

FROM python:3-slim
WORKDIR /app
RUN pip3 install gunicorn

COPY requirements3.txt /app/requirements3.txt
RUN pip3 install -r requirements3.txt

COPY --from=node-stage /app /app
COPY . /app
RUN python3 setup.py install

CMD [ "python3",  "amundsen_application/wsgi.py" ]
