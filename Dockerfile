FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Copia los scripts a un path fuera de /app
COPY app/scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY app/scripts/wait_for_db.py /usr/local/bin/wait_for_db.py

# Normaliza LF y permisos
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh /usr/local/bin/wait_for_db.py \
 && chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
