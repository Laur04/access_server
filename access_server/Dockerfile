FROM python:3.8.3-alpine as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
RUN pip install flake8
COPY . .
RUN flake8 --ignore=E501,F401 .

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


FROM python:3.8.3-alpine

RUN mkdir -p /home/access_server_user

RUN addgroup -S access_server_user && adduser -S access_server_user -G access_server_user

ENV HOME = /home/access_server_user
ENV APP_HOME=/home/access_server_user/access_server
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/serve
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

RUN apk update && apk add libpq
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.sh $APP_HOME

COPY . $APP_HOME

RUN chown -R access_server_user:access_server_user $APP_HOME

USER access_server_user

ENTRYPOINT ["/home/access_server_user/access_server/entrypoint.sh"]