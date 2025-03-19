FROM python:3.9-slim

WORKDIR /app
COPY boton/ /app/boton/
COPY requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/boton/entrypoint.py"]