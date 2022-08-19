FROM python:3.10.4-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV REDIS_HOST="redis"
ENV REDIS_PORT=6379

COPY ./requirements.txt ./requirements.txt
COPY  ./docker/supervisor /src/supervisor
COPY ./.env ./.env
COPY ./api ./api

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["supervisord","-c","/src/supervisor/service_script.conf"]