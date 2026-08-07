FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

ENV PYTHONPATH=/app:$PYTHONPATH

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/start.sh

EXPOSE 5000

CMD ["./start.sh"]
