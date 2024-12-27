FROM python:3.12-slim-bullseye

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Copy only the necessary files for dependency installation
COPY pyproject.toml poetry.lock ./


RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY src/ .
