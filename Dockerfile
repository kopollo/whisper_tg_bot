FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install --upgrade pip --no-cache-dir -r requirements.txt
ENV PYTHONPATH="/app"
COPY . /app
