FROM python:3.11-slim AS production

ARG RELEASE_SHA=unknown
ENV RELEASE_SHA=$RELEASE_SHA

COPY /start.sh /start.sh
RUN chmod +x /start.sh

COPY /start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

WORKDIR /app
EXPOSE 80

COPY /requirements.txt ./requirements.txt

# to build psycopg
RUN apt-get update \
    && apt-get install -y apt-utils libpq-dev gcc openssl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt

COPY . /app

CMD ["/start.sh"]

FROM production AS dev

COPY /requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r ./requirements-dev.txt
