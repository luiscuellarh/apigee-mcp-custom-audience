FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --compile -r requirements.txt \
    && useradd --create-home --shell /bin/bash appuser

COPY --chown=appuser:appuser main.py .

USER appuser
EXPOSE 8080
CMD ["python", "main.py"]
