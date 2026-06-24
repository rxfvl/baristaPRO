FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into backend package
COPY . /app/backend

# Create the startup script inline
RUN echo '#!/bin/bash\n\
python -c "from backend.database import engine, Base; import backend.models; Base.metadata.create_all(bind=engine)"\n\
uvicorn backend.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
