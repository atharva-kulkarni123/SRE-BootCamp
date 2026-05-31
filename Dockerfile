FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the app source code
COPY app/ .

EXPOSE 5000

# CMD ["python", "main.py"]
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "main:app"]