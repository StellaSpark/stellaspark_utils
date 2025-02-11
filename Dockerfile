FROM python:3.12.9-slim-bookworm 
LABEL maintainer="StellaSpark"

# Install Python and add code
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt 
COPY requirements_dev.txt .
RUN pip3 install -r requirements_dev.txt 
COPY requirements_test.txt .
RUN pip3 install -r requirements_test.txt 

# Make sure local python imports work
ENV PYTHONPATH="${PYTHONPATH}:${WORKDIR}"

COPY . /code/
CMD ["sleep", "infinity"]
