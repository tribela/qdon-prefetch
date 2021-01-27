FROM python:3.9

ENV PYTHON_UNBUFFERED=1
ENV PATH="${HOME}/.poetry/bin:${PATH}"
RUN pip install poetry
WORKDIR /src
COPY poetry.lock pyproject.toml /src/
RUN poetry config virtualenvs.create false \
        && poetry install --no-dev --no-interaction --no-ansi
ADD . /src

CMD ["python", "-u", "main.py"]
