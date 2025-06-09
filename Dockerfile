# Use official Python image as base
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install uv (for fast Python packaging and running)
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Install project dependencies using uv
RUN uv pip install --system --requirement pyproject.toml || uv pip install --system --requirement requirements.txt || true

# Expose the default port for streamable-http
EXPOSE 8000

# Run the weather MCP server
CMD ["uv", "run", "weather.py"]
