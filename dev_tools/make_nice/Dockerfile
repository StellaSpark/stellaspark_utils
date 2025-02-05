FROM python:3.7
LABEL maintainer="StellaSpark"

COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY pyproject.toml ./
COPY setup.cfg ./
