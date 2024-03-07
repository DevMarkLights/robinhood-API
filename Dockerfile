FROM python:3.9

WORKDIR /python-docker

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "flask", "run","--port","8080","--host","0.0.0.0"]