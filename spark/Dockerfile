FROM python:3.11-slim

# Install OpenJDK 17 and other utilities
RUN apt-get update && \
    mkdir -p /usr/share/man/man1 && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        procps \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "stream_processor.py"]
