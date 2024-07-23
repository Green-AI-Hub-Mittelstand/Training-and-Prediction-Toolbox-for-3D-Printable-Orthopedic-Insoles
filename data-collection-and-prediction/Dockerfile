FROM python:latest

ENV PYTHONUNBUFFERED=1

RUN mkdir /code

WORKDIR /code



COPY requirements.txt .
RUN pip install -r requirements.txt

# RUN pip install auto-sklearn

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 gettext  -y