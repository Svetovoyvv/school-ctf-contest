FROM python:3.12-alpine

WORKDIR /app

RUN apk add ffmpeg && pip install pydub

COPY app/ .
ENTRYPOINT ["python", "app.py"]
