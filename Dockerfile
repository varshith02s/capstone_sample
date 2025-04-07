FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .  # This copies the whole capstone_sample directory, including app/
CMD ["gunicorn", "-b", ":8080", "app.main:app"]
