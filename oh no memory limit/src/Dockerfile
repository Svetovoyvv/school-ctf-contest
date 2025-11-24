FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache \
    ttf-dejavu \
    zlib-dev \
    jpeg-dev \
    gcc \
    musl-dev \
    freetype-dev \
    git

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/Svetovoyvv/pngresize.git

COPY main.py .
COPY entrypoint.sh .
ENTRYPOINT [ "/bin/sh", "entrypoint.sh" ]


