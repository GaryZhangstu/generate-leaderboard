
FROM python:3.12.0


WORKDIR /app


COPY . /app




EXPOSE 8000

CMD pip install --no-cache-dir -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000
