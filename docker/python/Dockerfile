FROM python:3.13-slim

RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get install -y git \
    && pip install psycopg2 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /home/sites/
RUN mkdir /home/sites/Bookkeeping
WORKDIR /home/sites/Bookkeeping
ADD requirements.txt /home/sites/Bookkeeping
RUN pip install -r requirements.txt



# RUN apt-get update
# RUN apt update && apt install -y pkg-config gcc \
#     default-libmysqlclient-dev pkg-config
# RUN pip install mysqlclient==2.2.1



# RUN pip install --upgrade pip

# # Install Russian locales
# RUN apt-get update && \
#     apt-get install -y locales && \
#     echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen && \
#     locale-gen && \
#     update-locale LANG=ru_RU.UTF-8

# ENV LANG=ru_RU.UTF-8 \
#     LANGUAGE=ru_RU:ru \
#     LC_ALL=ru_RU.UTF-8



# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# RUN mkdir /home/sites/
# WORKDIR /home/sites/
# ADD requirements.txt /home/sites/
# RUN pip install -r requirements.txt