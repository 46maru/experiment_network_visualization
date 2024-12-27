FROM python:3.13.1-slim

WORKDIR /workspace
COPY ./requirements.txt /opt/requirements.txt

RUN pip install --upgrade pip && pip install --upgrade setuptools && pip install -r /opt/requirements.txt
