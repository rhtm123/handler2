FROM python:3.9-slim-buster
RUN apt-get update

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app/
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--worker-class", "uvicorn.workers.UvicornWorker", "app.asgi"]
# CMD ["python", "app.py", "-p","80","--host","0.0.0.0"]
# gunicorn --bind 0.0.0.0:5000 --worker-class uvicorn.workers.UvicornWorker mywebsite.asgi
