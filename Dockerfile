# Dockerfile
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x app/scripts/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["bash", "app/scripts/entrypoint.sh"]
