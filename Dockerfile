FROM python:3.11-slim

WORKDIR /app

COPY luna_api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY luna_api/* ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]