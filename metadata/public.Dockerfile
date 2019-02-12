FROM python:3
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

ENTRYPOINT [ "python3" ]
CMD [ "metadata_service/metadata_wsgi.py" ]
