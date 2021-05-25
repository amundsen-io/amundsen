FROM python:3.7-slim
WORKDIR /app
RUN pip3 install gunicorn

COPY ./search/ /app/
COPY requirements-dev.txt /app/requirements-dev.txt
COPY requirements-common.txt /app/requirements-common.txt
RUN pip3 install -e .

CMD [ "python3", "search_service/search_wsgi.py" ]
