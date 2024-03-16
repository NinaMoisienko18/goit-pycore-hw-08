FROM python

COPY . .

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="${PATH}:/root/.poetry/bin"
RUN cd /app && poetry install --no-dev

ENV PYTHONUNBUFFERED=1

WORKDIR /app

CMD ["python", "main_project.py"]