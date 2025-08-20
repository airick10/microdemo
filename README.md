# microdemo
1) Create a project and apply base objects
oc new-project microdemo
oc apply -f k8s-openshift/00-namespace.yaml
oc apply -f k8s-openshift/01-secrets.yaml
oc apply -f k8s-openshift/02-configmap.yaml

2)  Bring up Data Services
oc apply -f k8s-openshift/10-mysql-statefulset.yaml
oc apply -f k8s-openshift/11-redis-deployment.yaml
oc apply -f k8s-openshift/30-services.yaml

Wait for MySQL readiness before app pods:
oc get pods -n microdemo -w

3) Build images into internal registry
# API
oc new-build --name=api --binary --strategy=docker -n microdemo
oc start-build api --from-dir=services/api --follow -n microdemo


# Frontend
oc new-build --name=frontend --binary --strategy=docker -n microdemo
oc start-build frontend --from-dir=services/frontend --follow -n microdemo


# Worker
oc new-build --name=worker --binary --strategy=docker -n microdemo
oc start-build worker --from-dir=services/worker --follow -n microdemo

Verify imagestreams
oc get is -n microdemo

4) Deploy app pods and expose with Routes
oc apply -f k8s-openshift/20-api-deployment.yaml
oc apply -f k8s-openshift/21-frontend-deployment.yaml
oc apply -f k8s-openshift/22-worker-deployment.yaml
oc apply -f k8s-openshift/40-routes.yaml


5) Smoke test
oc get routes -n microdemo
# copy the frontend host and open it in your browser

Post a message in the UI.  Confirm it appears and survives refreshes.  Check the API Directly.
curl -s https://$(oc get route api -n microdemo -o jsonpath='{.spec.host}')/messages | jq .

6) What to practice next

Rolling updates: bump the frontend image by editing the Deployment or triggering a new Build

Readiness gates: break MySQL password and watch readiness fail

HPA: add resources and try a simple HPA on the API

Secrets: rotate the MySQL user password and restart worker + api

Logs: oc logs deploy/worker -f to watch queue consumption

Quotas and limits: constrain the namespace and test scheduling

7) Notes for air‑gapped clusters

Swap docker.io/library/mysql:8.0 and docker.io/library/redis:7 for your mirrored registry paths

Binary Builds avoid pulling from the internet. If you need BaseImages mirrored, update BuildConfig base in the generated ImageStream or use UBI images and a pip wheel cache

8) Cleanup
oc delete project microdemo
