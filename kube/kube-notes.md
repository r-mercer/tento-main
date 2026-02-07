# Notes

Still need to port forward
`kubectl port-forward -n tento svc/tento-mongodb-svc 27017:27017`

## Helm

- helm repo add bitnami https://charts.bitnami.com/bitnami
- helm search repo bitnami
- kubectl create secret generic tento-secret --from-literal=mongodb-passwords=PASSWORD --from-literal=mongodb-root-password=ROOT_PASSWORD --dry-run -o yaml | kubectl apply -f -
- INSTALL USING EITHER:
    - helm install -f values.yaml bitnami/wordpress
- Actually ended up using the mongo db community image detailed elsewhere.



### Reference

#### MongoDb
Container Reference: https://artifacthub.io/packages/helm/bitnami/mongodb
Helm values.local: https://github.com/rkazak07/Mongodb-Helm-Chart/blob/main/values-example.yaml


Misc

```
MongoDB&reg; can be accessed on the following DNS name(s) and ports from within your cluster:

    tento-mongodb.tento.svc.cluster.local

To get the root password run:

    export MONGODB_ROOT_PASSWORD=$(kubectl get secret --namespace tento tento-secret -o jsonpath="{.data.mongodb-root-password}" | base64 -d)

To get the password for "devUser" run:

    export MONGODB_PASSWORD=$(kubectl get secret --namespace tento tento-secret -o jsonpath="{.data.mongodb-passwords}" | base64 -d | awk -F',' '{print $1}')

To connect to your database, create a MongoDB&reg; client container:

    kubectl run --namespace tento tento-mongodb-client --rm --tty -i --restart='Never' --env="MONGODB_ROOT_PASSWORD=$MONGODB_ROOT_PASSWORD" --image docker.io/bitnami/mongodb:5.0.14-debian-11-r0 --command -- bash

Then, run the following command:
    mongosh admin --host "tento-mongodb" --authenticationDatabase admin -u $MONGODB_ROOT_USER -p $MONGODB_ROOT_PASSWORD

```
