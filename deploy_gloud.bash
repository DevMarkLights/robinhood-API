
#build docker image and send to registry
gcloud builds submit --region=us-central1 --tag us-east1-docker.pkg.dev/yf-api-468304/yf-api/yf-api:tag1
#run the image in container
gcloud run deploy yf-api --image=us-east1-docker.pkg.dev/yf-api-468304/yf-api/yf-api:tag1
