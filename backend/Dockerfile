FROM python:3.12-slim-bullseye

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN pip install --upgrade pip
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
COPY ./src/ ./src/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "--port", "8080"]
