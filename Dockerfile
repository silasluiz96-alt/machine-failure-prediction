FROM python:3.11-slim

WORKDIR /app

COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

COPY . .

ENV PORT=8000

CMD ["python", "-c", "import os; import subprocess; port = os.environ.get('PORT', '8000'); subprocess.run(['uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', port])"]
