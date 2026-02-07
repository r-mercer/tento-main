# MongoDB Kubernetes Operator Deployment Guide

## Overview

This guide covers the deployment of MongoDB Community Edition using the MongoDB Kubernetes Operator (MCK) in a Kubernetes cluster.

## Deployment Process

### Step 1: Add MongoDB Helm Repository

```bash
helm repo add mongodb https://mongodb.github.io/helm-charts
helm repo update
```

### Step 2: Install MongoDB Kubernetes Operator

```bash
helm install mongodb-operator mongodb/mongodb-kubernetes --namespace tento --create-namespace
```

Verify the operator is running:

```bash
kubectl wait --for=condition=available --timeout=120s deployment/mongodb-kubernetes-operator -n tento
kubectl get deployment mongodb-kubernetes-operator -n tento
```

### Step 3: Create MongoDB Community Resource

Create a file `mongodb-community.yaml` with your configuration (see Configuration Options below).

Apply the configuration:

```bash
kubectl apply -f mongodb-community.yaml
```

### Step 4: Verify Deployment

Check the MongoDB resource status:

```bash
kubectl get mongodbcommunity tento-mongodb -n tento
kubectl get pods -n tento -l app=tento-mongodb-svc
```

Wait for the deployment to be ready:

```bash
kubectl wait --for=condition=ready pod/tento-mongodb-0 -n tento --timeout=120s
```

### Step 5: Retrieve Connection Information

Get the connection strings from the generated secret:

```bash
kubectl get secret tento-mongodb-tento-local-devuser -n tento -o json | jq -r '.data | with_entries(.value |= @base64d)'
```

## Configuration Options

### Basic Configuration

The `mongodb-community.yaml` file contains the following key configuration sections:

#### Replica Set Configuration

```yaml
spec:
  members: 1              # Number of replica set members (1 for testing, 3+ for production)
  type: ReplicaSet        # Deployment type
  version: "5.0.14"       # MongoDB version
```

#### Security and Authentication

```yaml
security:
  authentication:
    modes: ["SCRAM"]      # Authentication mechanism
```

#### User Configuration

```yaml
users:
  - name: devUser                    # Username
    db: tento-local                  # Authentication database
    passwordSecretRef:               # Reference to existing Kubernetes secret
      name: tento-secret
      key: mongodb-passwords
    roles:
      - name: dbOwner                # Database owner role
        db: tento-local
      - name: clusterMonitor         # Monitoring role
        db: admin
    scramCredentialsSecretName: devuser-scram
```

#### Storage Configuration

```yaml
statefulSet:
  spec:
    volumeClaimTemplates:
      - metadata:
          name: data-volume
        spec:
          accessModes: ["ReadWriteOnce"]
          storageClassName: hostpath    # Storage class (adjust for your cluster)
          resources:
            requests:
              storage: 10Gi              # Storage size per pod
```

#### Additional MongoDB Configuration

```yaml
additionalMongodConfig:
  storage.wiredTiger.engineConfig.journalCompressor: zlib
```

## Connection Information

### Connection Strings

After deployment, connection strings are stored in a Kubernetes secret named:
`<metadata.name>-<auth-db>-<username>`

In this deployment: `tento-mongodb-tento-local-devuser`

**Standard Connection String:**
```
mongodb://devUser:LOCALPASSWORD@tento-mongodb-0.tento-mongodb-svc.tento.svc.cluster.local:27017/tento-local?replicaSet=tento-mongodb&ssl=false
```

**SRV Connection String:**
```
mongodb+srv://devUser:LOCALPASSWORD@tento-mongodb-svc.tento.svc.cluster.local/tento-local?replicaSet=tento-mongodb&ssl=false
```

### Using Connection Strings in Applications

Reference the connection string in your pod configuration:

```yaml
containers:
  - name: app
    env:
      - name: MONGODB_URI
        valueFrom:
          secretKeyRef:
            name: tento-mongodb-tento-local-devuser
            key: connectionString.standardSrv
```

## Common Operations

### Scaling the Replica Set

To change the number of members, edit the `mongodb-community.yaml` file:

```yaml
spec:
  members: 3  # Change to desired number
```

Then reapply:

```bash
kubectl apply -f mongodb-community.yaml
```

### Checking Status

View MongoDB resource status:

```bash
kubectl get mongodbcommunity tento-mongodb -n tento
kubectl describe mongodbcommunity tento-mongodb -n tento
```

View pod logs:

```bash
kubectl logs tento-mongodb-0 -n tento -c mongod
kubectl logs tento-mongodb-0 -n tento -c mongodb-agent
```

### Deleting the Deployment

Delete the MongoDB instance:

```bash
kubectl delete mongodbcommunity tento-mongodb -n tento
```

Delete associated PVCs (data will be lost):

```bash
kubectl delete pvc -n tento -l app=tento-mongodb-svc
```

Delete the operator:

```bash
helm uninstall mongodb-operator -n tento
```

## Important Notes

- For production deployments, use 3 or more replica set members for high availability
- Persistent Volume Claims (PVCs) are retained when deleting MongoDB resources to prevent data loss
- Always back up data before performing upgrades or major changes
- The operator automatically handles TLS/SSL configuration if enabled
- Storage class must support dynamic provisioning for automatic PVC creation

## Troubleshooting

### Pod Stuck in Pending

Check PVC status:
```bash
kubectl get pvc -n tento
kubectl describe pvc <pvc-name> -n tento
```

Ensure the storage class exists and can provision volumes.

### Replica Set Not Ready

Check operator logs:
```bash
kubectl logs -n tento deployment/mongodb-kubernetes-operator --tail=50
```

Check MongoDB pod logs:
```bash
kubectl logs tento-mongodb-0 -n tento -c mongod --tail=50
```

### Connection Issues

Verify the secret was created:
```bash
kubectl get secret tento-mongodb-tento-local-devuser -n tento
```

Ensure pods are running:
```bash
kubectl get pods -n tento -l app=tento-mongodb-svc
```

## Resources

- MongoDB Kubernetes Operator Documentation: https://www.mongodb.com/docs/kubernetes/current/
- MongoDB Community Documentation: https://github.com/mongodb/mongodb-kubernetes/tree/master/docs/mongodbcommunity
- Helm Chart Repository: https://github.com/mongodb/mongodb-kubernetes/tree/master/helm_chart
