# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.16
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user with a REAL home directory.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# We'll let adduser create the home for appuser automatically at /home/appuser.
# Now set HOME so Python libraries that rely on HOME know where to write.
ENV HOME=/home/appuser

# Install dependencies as root
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy code
COPY . .

# Create a folder for Numba’s cache
RUN mkdir -p /app/numba_cache

# Make sure the entire /app and /home/appuser are owned by appuser
RUN chown -R appuser:appuser /app /home/appuser

# Switch to non-privileged user
USER appuser

# Numba cache directory
ENV NUMBA_CACHE_DIR="/app/numba_cache"

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]