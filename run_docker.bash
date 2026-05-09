docker rm robinhood-api

docker build -t robinhood-api .

docker run -p 8081:8081 --name robinhood-api --restart unless-stopped robinhood-api