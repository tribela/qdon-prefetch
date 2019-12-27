FROM python:3.7-alpine

RUN pip install pipenv
ADD . /src
WORKDIR /src
RUN pipenv install --system --deploy

CMD python -u main.py
