FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY docker-entrypoint.sh docker-entrypoint.sh
COPY bot/ ./bot

ENTRYPOINT ["./docker-entrypoint.sh"]