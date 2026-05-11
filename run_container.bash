docker stop yf-api
docker rm  yf-api
docker build -t yf-api . 
docker run -d --name yf-api -p 8081:8081 yf-api
