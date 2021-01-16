# Deployment of non-production Amundsen on AWS ECS using aws-cli

The following is a set of instructions to run Amundsen on AWS Elastic Container Service. The current configuration is very basic but it is working. It is a migration of the docker-amundsen.yml to run on AWS ECS.

## Install ECS CLI

The first step is to install ECS CLI, please follow the instructions from AWS [documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_installation.html)

### Get your access and secret keys from IAM

```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/docs/instalation-aws-ecs
$ export AWS_ACCESS_KEY_ID=xxxxxxxx
$ export AWS_SECRET_ACCESS_KEY=xxxxxx
$ export AWS_PROFILE=profilename
```

For the purpose of this instruction we used the [tutorial](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-cli-tutorial-ec2.html#ECS_CLI_tutorial_compose_create) on AWS documentation

Enter the cloned directory:

```
cd amundsen/docs/installation-aws-ecs
```


## STEP 1: Create a cluster configuration:

```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/docs/instalation-aws-ecs
$ ecs-cli configure --cluster amundsen --region us-west-2 --default-launch-type EC2 --config-name amundsen
```

### STEP 2: Create a profile using your access key and secret key:

```bash
# in ~/<your-path-to-cloned-repo>/amundsen/docs/installation-aws-ecs
$ ecs-cli configure profile --access-key $AWS_ACCESS_KEY_ID --secret-key $AWS_SECRET_ACCESS_KEY --profile-name amundsen
```

### STEP 3: Create the Cluster Use profile name from \~/.aws/credentials

```bash
# in ~/<your-path-to-cloned-repo>/amundsen/docs/installation-aws-ecs
$ ecs-cli up --keypair JoaoCorreia --extra-user-data userData.sh --capability-iam --size 1 --instance-type t2.large --cluster-config amundsen --verbose --force --aws-profile $AWS_PROFILE
```

### STEP 4: Deploy the Compose File to a Cluster

```bash
# in ~/<your-path-to-cloned-repo>/amundsen/docs/installation-aws-ecs
$ ecs-cli compose --cluster-config amundsen --file docker-ecs-amundsen.yml up --create-log-groups
```

You can use the ECS CLI to see what tasks are running.

```bash
$ ecs-cli ps
```

### STEP 5 Open the EC2 Instance

Edit the Security Group to allow traffic to your IP, you should be able to see the frontend, elasticsearch and neo4j by visiting the URLs:

- http://xxxxxxx:5000/
- http://xxxxxxx:9200/
- http://xxxxxxx:7474/browser/

## TODO

- Configuration sent to services not working properly (amunsen.db vs graph.db)
- Create a persistent volume for graph/metadata storage. [See this](https://aws.amazon.com/blogs/compute/amazon-ecs-and-docker-volume-drivers-amazon-ebs/)
- Refactor the VPC and default security group permissions
