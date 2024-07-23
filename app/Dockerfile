# pull official base image
FROM python:3.12.4-alpine
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1
# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
# set work directory
WORKDIR /usr/src/app
# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# copy project
COPY . .
CMD python manage.py runserver 127.0.0.1:80 && celery -A cyclerent worker -l info