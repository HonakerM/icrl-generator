# Multi-stage build for ICRL Image Generator
# Stage 1: Builder - Install dependencies and build
FROM python:3.11-slim as build

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY .git .
COPY README.md .
COPY pyproject.toml .
COPY icrl_generator/ .

# Install dependencies to a specific directory
RUN pip install --no-cache-dir --no-compile --prefix=/install ".[aws]" 

# Stage 2: Runtime - Create minimal runtime image
FROM python:3.11-slim as release

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=build /install /usr/local

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/overlays

# Set the entrypoint to the module
ENTRYPOINT ["python", "-m", "icrl_generator"]

# Default command shows help
CMD ["--help"]