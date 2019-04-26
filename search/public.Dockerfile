FROM python:3
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt && python3 setup.py install

ENTRYPOINT [ "python3" ]
CMD [ "search_service/search_wsgi.py" ]
