FROM python:3.13-slim


RUN apt-get update
RUN apt update && apt install -y pkg-config gcc \
    default-libmysqlclient-dev pkg-config
RUN pip install mysqlclient==2.2.1



RUN pip install --upgrade pip

# Install Russian locales
RUN apt-get update && \
    apt-get install -y locales && \
    echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ru_RU.UTF-8

ENV LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru \
    LC_ALL=ru_RU.UTF-8

    
# RUN npm install --global less prettier

# RUN apt-get update \
#     && apt-get -y install libpq-dev gcc \
#     && pip install psycopg2 \
#     && apt-get -y install tesseract-ocr


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /home/sites/
WORKDIR /home/sites/
ADD requirements.txt /home/sites/
RUN pip install -r requirements.txt