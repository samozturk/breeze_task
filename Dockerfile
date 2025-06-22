# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install --upgrade pip && pip install uv

# Copy only the dependency file(s) first for better caching
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies using uv
RUN uv venv && uv pip install -e .

# Copy the rest of the application code
COPY . .

# Ensure the data directory exists
RUN mkdir -p data/input data/output

# Add volume for data directory
VOLUME ["/app/data"]

# Default command to run your app
CMD ["uv", "run", "main.py"]