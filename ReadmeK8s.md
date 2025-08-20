# Kubernetes Microdemo

A simple microservices demo app for Kubernetes. It includes:
- **MySQL** (persistent database with init script)
- **Redis** (cache and queue)
- **API** (Flask REST)
- **Frontend** (Flask web UI)
- **Worker** (background job processor)

## Prerequisites
- A default StorageClass that supports ReadWriteOnce for the MySQL PVC
- An Ingress controller (for example NGINX Ingress)
- A container registry the cluster can pull from, or a local image cache for dev

---

## 1. Create Project and Apply Base Objects

`kubectl apply -f k8s/00-namespace.yaml`

`kubectl apply -f k8s/01-secrets.yaml`

`kubectl apply -f k8s/02-configmap.yaml`


## 2.  Bring up Data Services
`kubectl apply -f k8s/10-mysql-statefulset.yaml`

`kubectl apply -f k8s/11-redis-deployment.yaml`

`kubectl apply -f k8s/30-services.yaml`

Wait for MySQL readiness before app pods:

`kubectl -n microdemo get pods -w`


## 3. Build images into a registry
API

`docker build -t emccumbe/microdemo-api:latest ./services/api`

`docker build -t emccumbe/microdemo-frontend:latest ./services/frontend`

`docker build -t emccumbe/microdemo-worker:latest ./services/worker`

`docker push emccumbe/microdemo-api:latest`

`docker push emccumbe/microdemo-frontend:latest`

`docker push emccumbe/microdemo-worker:latest`

## 4. Deploy app pods and expose with Routes
Install an ingress controller

`kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.1/deploy/static/provider/cloud/deploy.yaml`

`kubectl apply -f k8s/20-api-deployment.yaml`

`kubectl apply -f k8s/21-frontend-deployment.yaml`

`kubectl apply -f k8s/22-worker-deployment.yaml`

`kubectl apply -f k8s/40-ingress.yaml`


## 5. Smoke test
copy the frontend host and open it in your browser

`kubectl -n microdemo get ingress microdemo`

Post a message in the UI.  Confirm it appears and survives refreshes.  Check the API Directly.

`curl -s http://microdemo.<INGRESS_IP>.nip.io/api/messages | jq .`

## 6. What to practice next

Rolling updates: bump the frontend image by editing the Deployment or triggering a new Build

Readiness gates: break MySQL password and watch readiness fail

HPA: add resources and try a simple HPA on the API

Secrets: rotate the MySQL user password and restart worker + api

Logs: oc logs deploy/worker -f to watch queue consumption

Quotas and limits: constrain the namespace and test scheduling

## 7. Notes for air‑gapped clusters

Swap docker.io/library/mysql:8.0 and docker.io/library/redis:7 for your mirrored registry paths

Binary Builds avoid pulling from the internet. If you need BaseImages mirrored, update BuildConfig base in the generated ImageStream or use UBI images and a pip wheel cache

## 8. Cleanup

`kubectl delete namespace microdemo`
