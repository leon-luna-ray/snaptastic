# Stage 1: Build the frontend
# FROM node:18 AS frontend-builder

# WORKDIR /app/frontend

# # Copy frontend source code
# COPY frontend/package.json frontend/yarn.lock ./
# RUN yarn install
# COPY frontend/ ./
# RUN yarn build

# Stage 2: Build the backend
FROM python:3.10-slim AS backend-builder

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Copy the rest of the application code to the container
COPY . /app

# Stage 3: Final stage
# FROM python:3.10-slim

# Set the working directory in the container
# WORKDIR /app

# Copy the backend build from the previous stage
# COPY --from=backend-builder /app /app

# Copy the frontend build from the previous stage
# COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
# 
# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]