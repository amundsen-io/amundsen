# Amundsen K8s Helm Charts

Source code can be found [here](https://github.com/amundsen-io/amundsen)

## What is this?

This is setup templates for deploying [amundsen](https://github.com/amundsen-io/amundsen) on [k8s (kubernetes)](https://kubernetes.io/), using [helm.](https://helm.sh/)

## How do I get started?

1. Make sure you have the following command line clients setup:
    - k8s (kubectl)
    - helm
2. Build out a cloud based k8s cluster, such as [Amazon EKS](https://aws.amazon.com/eks/)
3. Ensure you can connect to your cluster with cli tools in step 1.

## Prerequisites

1. Helm 2.14+
2. Kubernetes 1.14+

## Chart Requirements

Note we updated from elasticsearch 6 to elasticsearch 7 

| Repository | Name | Version |
|------------|------|---------|
| https://helm.elastic.co | elasticsearch | 7.13.4 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| LONG_RANDOM_STRING | int | `1234` | A long random string. You should probably provide your own. This is needed for OIDC. |
| affinity | object | `{}` | amundsen application wide configuration of affinity. This applies to search, metadata, frontend and neo4j. Elasticsearch has it's own configuation properties for this. [ref](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity) |
| clusterDomain | string | `"cluster.local"` |  |
| dnsZone | string | `"teamname.company.com"` | **DEPRECATED - its not standard to pre construct urls this way.** The dns zone (e.g. group-qa.myaccount.company.com) the app is running in. Used to construct dns hostnames (on aws only). |
| dockerhubImagePath | string | `"amundsendev"` | **DEPRECATED - this is not useful, it would be better to just allow the whole image to be swapped instead.** The image path for dockerhub. |
| elasticsearch.enabled | bool | `true` | set this to false, if you want to provide your own ES instance. |
| elasticsearch.esJavaOpts | string | `"-Xmx8g -Xms8g"` | set init memory size (Xms) and maximum memory size (Xmx) for the es jvm. |
| elasticsearch.fullnameOverride | string | `"amundsen-elasticsearch-master"` | this is the service name of the amundsen elasticsearch master. Change it if you want to give a new name for the elasticsearch service   |
| elasticsearch.image | string | `"elasticsearch"` | elasticsearch docker image name |
| elasticsearch.resources | object | `{"limits":{"memory":"15Gi"},"requests":{"memory":"10Gi"}}` | set the pod resources |
| elasticsearch.sysctlInitContainer | object | `{"enabled":false}` | If this set to true, the es pod will require some admin privilege, which is not allowed in most case. So set it to false |
| environment | string | `"dev"` | **DEPRECATED - its not standard to pre construct urls this way.** The environment the app is running in. Used to construct dns hostnames (on aws only) and ports. |
| flaskApp.class | string | `""` | The class name within the flaskApp.module |
| flaskApp.module | string | `""` | Any custom flask module you may need to implement as a wrapper |
| frontEnd.ALL_UNEDITABLE_SCHEMAS | string | `nil` | Environment variable for allowing/disallowing editing schemas via the UI. All schemas are allowed to be edited by default. Set to 'true' to disallow. See https://www.amundsen.io/amundsen/frontend/docs/flask_config/#uneditable-table-descriptions for more |
| frontEnd.affinity | object | `{}` | Frontend pod specific affinity. |
| frontEnd.annotations | object | `{}` | Frontend service specific tolerations. |
| frontEnd.baseUrl | string | `"http://localhost"` | used by notifications util to provide links to amundsen pages in emails. |
| frontEnd.config.class | string | `nil` | Optional Config class. |
| frontEnd.envVars | object | `{}` |  |
| frontEnd.image | string | `"amundsendev/amundsen-frontend"` | The image of the frontend container. |
| frontEnd.imagePullSecrets | list | `[]` | Optional pod imagePullSecrets [ref](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) |
| frontEnd.imageTag | string | `"latest"` | The image tag of the frontend container. |
| frontEnd.nodeSelector | object | `{}` | Frontend pod specific nodeSelector. |
| frontEnd.podAnnotations | object | `{}` | Frontend pod specific annotations. |
| frontEnd.replicas | int | `1` | How many replicas of the frontend service to run. |
| frontEnd.resources | object | `{}` | See pod resourcing [ref](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/) |
| frontEnd.serviceName | string | `"frontend"` | The frontend service name. |
| frontEnd.servicePort | int | `80` | The port the frontend service will be exposed on via the loadbalancer. |
| frontEnd.serviceType | string | `"ClusterIP"` | The frontend service type. See service types [ref](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) |
| frontEnd.tolerations | list | `[]` | Frontend pod specific tolerations. |
| ingress.annotations | object | `{}` |  |
| ingress.enabled | bool | `true` | set this to true, if you want a ingress that expose HTTP and HTTPS routes from outside the cluster to your amundsen services. Don't use this if you are in a public cloud such as AWS, GCP |
| ingress.hosts[0].host | string | `"amundsen-test.your-domain.com"` |  |
| ingress.hosts[0].paths[0] | string | `"/"` |  |
| ingress.tls[0].hosts[0] | string | `"amundsen-test.your-domain.com"` |  |
| metadata.affinity | object | `{}` | Metadata pod specific affinity. |
| metadata.annotations | object | `{}` | Metadata service specific tolerations. |
| metadata.envVars | object | `{}` |  |
| metadata.image | string | `"amundsendev/amundsen-metadata"` | The image of the metadata container. |
| metadata.imagePullSecrets | list | `[]` | Optional pod imagePullSecrets [ref](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) |
| metadata.imageTag | string | `"latest"` | The image tag of the metadata container. |
| metadata.nodeSelector | object | `{}` | Metadata pod specific nodeSelector. |
| metadata.podAnnotations | object | `{}` | Metadata pod specific annotations. |
| metadata.proxy.host | string | `nil` | host name / URI of your proxy |
| metadata.proxy.password | string | `nil` | Credentials - Password of the proxy |
| metadata.proxy.port | string | `nil` | Port on which the proxy is running |
| metadata.proxy.user | string | `nil` | Credentials - Username of the proxy |
| metadata.replicas | int | `1` | How many replicas of the metadata service to run. |
| metadata.resources | object | `{}` | See pod resourcing [ref](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/) |
| metadata.serviceName | string | `"metadata"` | The metadata service name. |
| metadata.serviceType | string | `"ClusterIP"` | The metadata service type. See service types [ref](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) |
| metadata.tolerations | list | `[]` | Metadata pod specific tolerations. |
| neo4j.affinity | object | `{}` | neo4j specific affinity. |
| neo4j.annotations | object | `{}` | neo4j service specific tolerations. |
| neo4j.backup | object | `{"enabled":false,"podAnnotations":{},"s3Path":"s3://dev/null","schedule":"0 * * * *"}` | If enabled is set to true, make sure and set the s3 path as well. |
| neo4j.backup.s3Path | string | `"s3://dev/null"` | The s3path to write to for backups. |
| neo4j.backup.schedule | string | `"0 * * * *"` | The schedule to run backups on. Defaults to hourly. |
| neo4j.config | object | `{"dbms":{"heap_initial_size":"1G","heap_max_size":"2G","pagecache_size":"2G"}}` | Neo4j application specific configuration. This type of configuration is why the charts/stable version is not used. See [ref](https://github.com/helm/charts/issues/21439) |
| neo4j.config.dbms | object | `{"heap_initial_size":"1G","heap_max_size":"2G","pagecache_size":"2G"}` | dbms config for neo4j |
| neo4j.config.dbms.heap_initial_size | string | `"1G"` | the initial java heap for neo4j |
| neo4j.config.dbms.heap_max_size | string | `"2G"` | the max java heap for neo4j |
| neo4j.config.dbms.pagecache_size | string | `"2G"` | the page cache size for neo4j |
| neo4j.enabled | bool | `true` | If neo4j is enabled as part of this chart, or not. Set this to false if you want to provide your own version. |
| neo4j.image | string | `"neo4j"` | The image of the neo4j container. |
| neo4j.imageTag | string | `"3.3.0"` | The image tag of the neo4j container. |
| neo4j.initPluginsContainer.image | string | `"appropriate/curl"` | The image of the init neo4j plugins container. |
| neo4j.initPluginsContainer.imageTag | string | `"latest"` | The image tag of the init neo4j plugins container. |
| neo4j.initPluginsContainer.command | list | _See values.yaml_ | The command to execute in the init neo4j plugins container. |
| neo4j.nodeSelector | object | `{}` | neo4j specific nodeSelector. |
| neo4j.persistence | object | `{}` | Neo4j persistence. Turn this on to keep your data between pod crashes, etc. This is also needed for backups. |
| neo4j.podAnnotations | object | `{}` | neo4j pod specific annotations. |
| neo4j.resources | object | `{}` | See pod resourcing [ref](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/) |
| neo4j.serviceType | string | `"ClusterIP"` | The neo4j service type. See service types [ref](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) |
| neo4j.tolerations | list | `[]` | neo4j specific tolerations. |
| neo4j.version | string | `"3.3.0"` | **DEPRECATED - Now using the neo4j.imageTag** The neo4j application version used by amundsen. |
| nodeSelector | object | `{}` | amundsen application wide configuration of nodeSelector. This applies to search, metadata, frontend and neo4j. Elasticsearch has it's own configuation properties for this. [ref](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#nodeselector) |
| oidc.configs.FLASK_OIDC_CONFIG_URL | string | `"https://accounts.google.com/.well-known/openid-configuration"` |  |
| oidc.configs.FLASK_OIDC_PROVIDER_NAME | string | `"google"` |  |
| oidc.configs.FLASK_OIDC_REDIRECT_URI | string | `"/auth"` |  |
| oidc.configs.FLASK_OIDC_SCOPES | string | `"openid email profile"` |  |
| oidc.configs.FLASK_OIDC_USER_ID_FIELD | string | `"email"` |  |
| oidc.configs.FLASK_OIDC_WHITELISTED_ENDPOINTS | string | `"status,healthcheck,health"` |  |
| oidc.enabled | bool | `false` | flag to enable/disable the OIDC. Once enabled,   - everything under oidc.configs will be parsed   - flaskApp.module will be set as 'flaskoidc'   - flaskApp.class will be set as 'FlaskOIDC' |
| oidc.frontend.client_id | string | `""` |  |
| oidc.frontend.client_secret | string | `""` |  |
| oidc.metadata.client_id | string | `""` |  |
| oidc.metadata.client_secret | string | `""` |  |
| oidc.search.client_id | string | `""` |  |
| oidc.search.client_secret | string | `""` |  |
| podAnnotations | object | `{}` | amundsen application wide configuration of podAnnotations. This applies to search, metadata, frontend and neo4j. Elasticsearch has it's own configuation properties for this. [ref](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) |
| provider | string | `"aws"` | The cloud provider the app is running in. Used to construct dns hostnames (on aws only). |
| search.affinity | object | `{}` | Search pod specific affinity. |
| search.annotations | object | `{}` | Search service specific tolerations. |
| search.envVars | object | `{}` |  |
| search.image | string | `"amundsendev/amundsen-search"` | The image of the search container. |
| search.imagePullSecrets | list | `[]` | Optional pod imagePullSecrets [ref](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) |
| search.imageTag | string | `"latest"` | The image tag of the search container. |
| search.nodeSelector | object | `{}` | Search pod specific nodeSelector. |
| search.podAnnotations | object | `{}` | Search pod specific annotations. |
| search.proxy.endpoint | string | `nil` | Endpoint of the search proxy (i.e., ES endpoint etc.) You should only need to change this, if you don't use the version in this chart. elasticsearch-master.user-pengfei.svc.cluster.local |
| search.proxy.password | string | `nil` |  |
| search.proxy.user | string | `nil` |  |
| search.replicas | int | `1` | How many replicas of the search service to run. |
| search.resources | object | `{}` | See pod resourcing [ref](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/) |
| search.serviceName | string | `"search"` | The search service name. |
| search.serviceType | string | `"ClusterIP"` | The search service type. See service types [ref](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) |
| search.tolerations | list | `[]` | Search pod specific tolerations. |
| tolerations | list | `[]` | amundsen application wide configuration of tolerations. This applies to search, metadata, frontend and neo4j. Elasticsearch has it's own configuation properties for this. [ref](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#taints-and-tolerations-beta-feature) |


----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.5.0](https://github.com/norwoodj/helm-docs/releases/v1.5.0)

## Ingress support
If you want to deploy Amundsen on a K8s cluster on premise. You can activate the ingress module. Do not active ingress if you are using a public cloud such as AWS, GCP, etc.

``` yaml
ingress:
  enabled: true
  annotations: {}
  hosts:
    - host: amundsen-test.your-domain.com
      paths: [/]
  tls: 
    - hosts:
        - amundsen-test.your-domain.com
```

## Neo4j DBMS Config?

You may want to override the default memory usage for Neo4J. In particular, if you're just test-driving a deployment and your node exits with status 137, you should set the usage to smaller values:

``` yaml
config:
  dbms:
    heap_initial_size: 1G
    heap_max_size: 2G
    pagecache_size: 2G
```

With this values file, you can then install Amundsen using Helm 2 with:

``` shell
helm install ./templates/helm --values impl/helm/dev/values.yaml
```

For Helm 3 it's now mandatory to specify a [chart reference name](https://helm.sh/docs/intro/using_helm/#helm-install-installing-a-package) e.g. `my-amundsen`:

``` shell
helm install my-amundsen ./templates/helm --values impl/helm/dev/values.yaml
```

## Other Notes

- For aws setup, you will also need to setup the [external-dns plugin](https://github.com/kubernetes-incubator/external-dns)
- There is an existing helm chart for neo4j, but, it is missing some features necessary to for use such as:
  - [\[stable/neo4j\] make neo4j service definition more extensible](https://github.com/helm/charts/issues/21441); without this, it is not possible to setup external load balancers, external-dns, etc
  - [\[stable/neo4j\] allow custom configuration of neo4j](https://github.com/helm/charts/issues/21439); without this, custom configuration is not possible which includes setting configmap based settings, which also includes turning on apoc.
