FROM python:3
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
RUN python3 setup.py install
RUN pip3 install gunicorn

CMD [ "python3", "metadata_service/metadata_wsgi.py" ]
