
#build docker image and send to registry
gcloud builds submit --region=us-central1 --tag us-east1-docker.pkg.dev/lightsfinance/lights-finance-docker-repo/robinhood_api:tag1
#run the image in container
gcloud run deploy --image=us-east1-docker.pkg.dev/lightsfinance/lights-finance-docker-repo/robinhood_api:tag1
