FROM python:3.13-slim


RUN apt-get update
RUN apt update && apt install -y pkg-config gcc \
    default-libmysqlclient-dev pkg-config
RUN pip install mysqlclient==2.2.1



RUN pip install --upgrade pip
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