FROM python:3.12.9-slim-bookworm
LABEL maintainer="StellaSpark"

WORKDIR /code

COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
