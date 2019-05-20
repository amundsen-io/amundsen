FROM node:8 as node-stage

COPY . /app

WORKDIR /app/amundsen_application/static

RUN npm install
RUN npm run build

FROM python:3

COPY --from=node-stage /app /app

WORKDIR /app

RUN pip3 install -r requirements3.txt
RUN python3 setup.py install

ENTRYPOINT [ "python3" ]
CMD [ "amundsen_application/wsgi.py" ]
