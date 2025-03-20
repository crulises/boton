FROM python:3.9-slim

WORKDIR /app
COPY boton/ /app/boton/
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONPATH=/app

ENTRYPOINT ["python", "/app/boton/entrypoint.py"]