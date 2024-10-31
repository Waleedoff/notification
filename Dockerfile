FROM python:3.11-slim AS production


ENV MODULE_NAME=app.main:app
ENV PYTHONPATH=/app
ENV WORKER_CLASS=uvicorn.workers.UvicornWorker

ARG RELEASE_SHA=unknown
ENV RELEASE_SHA=$RELEASE_SHA

ENV SQLALCHEMY_WARN_20=true

COPY /start.sh /start.sh
RUN chmod +x /start.sh

COPY /start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

WORKDIR /app
EXPOSE 80

COPY /requirements.txt ./requirements.txt

# to build psycopg2
RUN apt-get update \
    && apt-get install -y libpq-dev gcc openssl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    pip install --no-cache-dir -r ./requirements.txt

COPY . /app

CMD ["/start.sh"]

FROM production AS dev

RUN pip install -r ./requirements-dev.txt

