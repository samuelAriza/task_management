FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV USE_SQLITE=true

CMD ["python", "-m", "uvicorn", "app.adapters.http.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]