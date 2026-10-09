FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/aftabahmad019/headercheck"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY headercheck.py .

RUN useradd --create-home appuser
USER appuser

ENTRYPOINT ["python", "headercheck.py"]