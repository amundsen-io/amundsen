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

Local data is persisted under [.local/](../.local/), clean up those directories to reset the databases

```bash
#  reset elasticsearch
rm -rf .local/elasticsearch

#  reset neo4j
rm -rf .local/neo4j
```


### Troubleshooting
1. If you have made a change in `amundsen/amundsenfrontendlibrary` and do not see your changes, this could be due to your browser's caching behaviors. Either execute a hard refresh (recommended) or clear your browser cache (last resort).
