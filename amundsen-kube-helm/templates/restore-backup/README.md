# Restoring neo4j Backups

The Amundsen Helm chart includes a Kubernetes CronJob that backs up the neo4j database to S3. If you need to restore from one of these backups, use the one-off pod in this directory.

## Create the Pod

You should have setup `kubectl` for the Kubernetes cluster you wish to restore in before running these commands.

Update the YAML file with the S3 Bucket for the backup you wish to restore and then apply the pod.

```shell
kubectl apply -n <your-namespace> -f restore-neo4j-pod.yaml
```

Once the pod has been created, it will automatically run the restore. You can check the pod's logs to see whether it has succeeded for failed.
