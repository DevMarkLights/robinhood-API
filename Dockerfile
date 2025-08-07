FROM python:3.9

WORKDIR /python-docker

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# ENV FLASK_APP=app.py
# ENV FLASK_RUN_PORT=8080
# ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 8080

# CMD ["python", "-m", "flask", "run","--port","8080","--host","0.0.0.0"]
# CMD ["flask", "run"]
CMD ["python", "app.py"]