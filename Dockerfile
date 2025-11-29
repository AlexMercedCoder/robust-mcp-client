# Stage 1: Build UI
FROM node:18-alpine AS ui-build
WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm install
COPY ui/ ./
RUN npm run build

# Stage 2: Python Runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for building llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
# Use a pre-built wheel for llama-cpp-python if possible to save build time, 
# but falling back to build is safer with build-essential installed.
# We set CMAKE_ARGS to enable basic CPU support (default).
RUN CMAKE_ARGS="-DLLAMA_BLAS=OFF" pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY cli/ ./cli/
COPY server/ ./server/
COPY mcp.json .

# Copy built UI from Stage 1
COPY --from=ui-build /app/ui/dist ./ui/dist

# Create directory for models and database
RUN mkdir -p models

# Expose port
EXPOSE 8000

# Environment variables
ENV HOST=0.0.0.0
ENV PORT=8000

# Run the server
CMD ["python", "-m", "cli.main", "serve"]
