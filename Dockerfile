FROM python:3.9-slim
ENV TZ "Asia/Bangkok"

RUN apt -y update
RUN apt-get -y update
RUN apt-get install build-essential -y

WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY install_lib.sh /app/install_lib.sh
RUN cdmod 755 install_lib.sh
RUN ./install_lib.sh
COPY . /app
WORKDIR /app
