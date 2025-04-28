FROM python:3.12-slim


# RUN apt-get update
# RUN apt-get install default-mysql-client -y



RUN pip install --upgrade pip
# RUN npm install --global less prettier

# RUN apt-get update \
#     && apt-get -y install libpq-dev gcc \
#     && pip install psycopg2 \
#     && apt-get -y install tesseract-ocr


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /home/sites/
RUN mkdir /home/sites/lemurproj
WORKDIR /home/sites/lemurproj
ADD requirements.txt /home/sites/lemurproj
RUN pip install -r requirements.txt