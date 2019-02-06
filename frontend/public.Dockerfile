FROM python:3
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements3.txt
RUN python3 setup.py install

ENTRYPOINT [ "python3" ]
CMD [ "amundsen_application/wsgi.py" ]
