FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Configure poetry to not create virtualenvs inside the container
RUN poetry config virtualenvs.create false

# Copy dependency definitions
COPY pyproject.toml ./

# Install dependencies
# We look for poetry.lock but if it's not present, it will just use pyproject.toml
COPY poetry.lock* ./
RUN poetry install --no-root --only main

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
