FROM python:3.12-alpine

WORKDIR /app

RUN pip install jinja2

COPY ./app .

ENTRYPOINT ["python", "app.py"]
