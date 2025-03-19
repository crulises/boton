FROM python:3.9-slim

WORKDIR /app
COPY boton/ /app/boton/
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["echo", "sys.path.append('/app/boton')", ">", "/app/update_sys.py"]
CMD ["python", "/app/update_sys.py"]

ENTRYPOINT ["python", "/app/boton/entrypoint.py"]