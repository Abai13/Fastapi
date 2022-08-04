FROM python:3.8
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./app ./app
COPY requirements.txt ./requirements.txt
COPY ./init-user-db.sh /docker-entrypoint-initdb.d/init-user-db.sh
RUN pip install -r requirements.txt --upgrade pip