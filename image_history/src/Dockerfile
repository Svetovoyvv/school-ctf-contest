FROM python:3.12-alpine

WORKDIR /app

RUN apk add exiftool

COPY src.jpg .
COPY app.py .

ENTRYPOINT ["python", "app.py"]


