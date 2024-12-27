FROM python:3.12-slim-bullseye

RUN mkdir /app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN pip install --upgrade pip
RUN pip install virtualenv

COPY requirements.txt ./
COPY ./src/ ./src/

RUN virtualenv venv
RUN . venv/bin/activate && pip install -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "--port", "8080"]