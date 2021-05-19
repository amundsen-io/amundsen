# Installation

## Install standalone application directly from the source

The following instructions are for setting up a standalone version of the Amundsen application. This approach is ideal for local development.
```bash
# Clone repo
$ git clone https://github.com/lyft/amundsenfrontendlibrary.git

# Build static content
$ cd amundsenfrontendlibrary/amundsen_application/static
$ npm install
$ npm run build # or npm run dev-build for un-minified source
$ cd ../../

# Install python resources
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ python3 setup.py install

# Start server
$ python3 amundsen_application/wsgi.py
# visit http://localhost:5000 to confirm the application is running
```

You should now have the application running at http://localhost:5000, but will notice that there is no data and interactions will throw errors. The next step is to connect the standalone application to make calls to the search and metadata services.
1. Setup a local copy of the metadata service using the instructions found [here](https://github.com/lyft/amundsenmetadatalibrary).
2. Setup a local copy of the search service using the instructions found [here](https://github.com/lyft/amundsensearchlibrary).
3. Modify the `LOCAL_HOST`, `METADATA_PORT`, and `SEARCH_PORT` variables in the [LocalConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) to point to where your local metadata and search services are running, and restart the application with
```bash
$ python3 amundsen_application/wsgi.py
```
