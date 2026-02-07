FROM python:3.13-slim

WORKDIR /project

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Write Firebase credentials from env var to file at runtime (if provided as JSON string)
# This allows setting FIREBASE_CREDENTIALS_JSON as an Aedify env var
CMD ["sh", "-c", "\
  if [ -n \"$FIREBASE_CREDENTIALS_JSON\" ]; then \
    echo \"$FIREBASE_CREDENTIALS_JSON\" > /project/firebase-key.json; \
  fi && \
  gunicorn wsgi:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120\
"]
