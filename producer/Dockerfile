FROM python:3.12-slim

WORKDIR /app

COPY producer.py .

RUN pip install psycopg2-binary

CMD ["python", "producer.py"]
