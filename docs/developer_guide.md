# Developer Guide

This repository uses `git submodules` to link the code for all of Amundsen's libraries into a central location. This document offers guidance on how to develop locally with this setup.

This workflow leverages `docker` and `docker-compose` in a very similar manner to our [installation documentation](https://github.com/lyft/amundsen/blob/master/docs/installation.md#bootstrap-a-default-version-of-amundsen-using-docker), to spin up instances of all 3 of Amundsen's services connected with an instances of Neo4j and ElasticSearch which ingest dummy data.

## Cloning the Repository

If cloning the repository for the first time, run the following command to clone the repository and pull the submodules:
```bash
$ git clone --recursive git@github.com:lyft/amundsen.git
```

If  you have already cloned the repository but your submodules are empty, from your cloned `amundsen` directory run:
```bash
$ git submodule init
$ git submodule update
```

After cloning the repository you can change directories into any of the upstream folders and work in those directories as you normally would. You will have full access to all of the git features, and working in the upstream directories will function the same as if you were working in a cloned version of that repository.

## Local Development

### Ensure you have the latest code
Beyond running `git pull origin master` in your local `amundsen` directory, the submodules for our libraries also have to be manually updated to point to the latest versions of each libraries' code. When creating a new branch on `amundsen` to begin local work, ensure your local submodules are pointing to the latest code for each library by running:
```bash
$ git submodule update --remote
```

### Building local changes
1. First, be sure that you have first followed the [installation documentation](https://github.com/lyft/amundsen/blob/master/docs/installation.md#bootstrap-a-default-version-of-amundsen-using-docker) and can spin up a default version of Amundsen without any issues. If you have already completed this step, be sure to have stopped and removed those containers by running:
    ```bash
    $ docker-compose -f docker-amundsen.yml down
    ```
2. Launch the containers needed for local development (the `-d` option launches in background) :
    ```bash
    $ docker-compose -f docker-amundsen-local.yml up -d
    ```
3. After making local changes rebuild and relaunch modified containers:
    ```bash
    $ docker-compose -f docker-amundsen-local.yml build \
      && docker-compose -f docker-amundsen-local.yml up -d
    ```
4. Optionally, to still tail logs, in a different terminal you can:
    ```bash
    $ docker-compose -f docker-amundsen-local.yml logs --tail=3 -f
    ## - or just tail single container(s):
    $ docker logs amundsenmetadata --tail 10 -f
    ```

### Local data

Local data is persisted under .local/ (at the root of the project), clean up the following directories to reset the databases:

```bash
#  reset elasticsearch
rm -rf .local/elasticsearch

#  reset neo4j
rm -rf .local/neo4j
```


### Troubleshooting
1. If you have made a change in `amundsen/amundsenfrontendlibrary` and do not see your changes, this could be due to your browser's caching behaviors. Either execute a hard refresh (recommended) or clear your browser cache (last resort).



### Testing Amundsen frontend locally

Amundsen has an instruction regarding local frontend launch [here](https://github.com/lyft/amundsenfrontendlibrary/blob/master/docs/installation.md)

Here are some additional changes you might need for windows (OS Win 10):

 - amundsen_application/config.py, set LOCAL_HOST = '127.0.0.1'
 - amundsen_application/wsgi.py, set host='127.0.0.1'
 (for other microservices also need to change `port` here because the default is 5000)

(using that approach you can run locally another microservices as well if needed)  

Once you have a running frontend microservice, the rest of Amundsen components can be launched with docker-compose 
from the root Amundsen project (don't forget to remove frontend microservice section from docker-amundsen.yml):
`docker-compose -f docker-amundsen.yml up`
https://github.com/lyft/amundsen/blob/master/docs/installation.md

### Developing Dockerbuild file

When making edits to Dockerbuild file (docker-amundsen-local.yml) it is good to see what you are getting wrong locally.
To do that you build it `docker build .`

And then the output should include a line like so at the step right before it failed:
```bash
Step 3/20 : RUN git clone --recursive git://github.com/lyft/amundsenfrontendlibrary.git  && cd amundsenfrontendlibrary  && git submodule foreach git pull origin master
 ---> Using cache
 ---> ec052612747e
```

You can then launch a container from this image like so
```bash
docker container run -it --name=debug ec052612747e /bin/sh
```

### Building and Testing Amundsen Frontend Docker Image (or any other service)

1. Build your image
`docker build --no-cache .` it is recommended that you use --no-cache so you aren't accidentally using an old version of an image.
2. Determine the hash of your images by running `docker images` and getting the id of your most recent image
3. Go to your locally cloned amundsen repo and edit the docker compose file "docker-amundsen.yml" to have 
the amundsenfrontend image point to the hash of the image that you built

```yaml
  amundsenfrontend:
      #image: amundsendev/amundsen-frontend:1.0.9
      #image: 1234.dkr.ecr.us-west-2.amazonaws.com/edmunds/amundsen-frontend:2020-01-21
      image: 0312d0ac3938
```


### Pushing image to ECR and using in K8s

Assumptions:
- You have an aws account
- You have aws command line set up and ready to go

1. Choose an ECR repository you'd like to push to (or create a new one)
https://us-west-2.console.aws.amazon.com/ecr/repositories
2. Click onto repository name and open "View push commands" cheat sheet
2b. Login
    
    it would look something like this:
   
    `aws ecr get-login --no-include-email --region us-west-2`
    Then execute what is returned by above
    
3. Follow the instructions (you may need to install first AWS CLI, aws-okta and configure your AWS credentials if you haven't done it before)
Given image name is amundsen-frontend, build, tag and push commands will be the following:
Here you can see the tag is YYYY-MM-dd but you should choose whatever you like. 
    ```
    docker build -t amundsen-frontend:{YYYY-MM-dd} .
    docker tag amundsen-frontend:{YYYY-MM-dd} <?>.dkr.ecr.<?>.amazonaws.com/amundsen-frontend:{YYYY-MM-dd}
    docker push <?>.dkr.ecr.<?>.amazonaws.com/amundsen-frontend:{YYYY-MM-dd}
    ```

4. Go to the `helm/{env}/amundsen/values.yaml` and modify to the image tag that you want to use.


5. When updating amundsen-frontend, make sure to do a hard refresh of amundsen with emptying the cache,
otherwise you will see stale version of webpage.
