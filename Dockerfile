FROM python:3.11-slim

WORKDIR /app

COPY parking_lot.py .

CMD ["python", "-u", "parking_lot.py"]
