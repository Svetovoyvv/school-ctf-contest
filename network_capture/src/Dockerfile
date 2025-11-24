FROM python:3.12-slim

WORKDIR /app

# Install tshark and dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tshark \
    vsftpd \
    && rm -rf /var/lib/apt/lists/*

COPY generate_challenge.py .

ENTRYPOINT ["python3", "generate_challenge.py"]

