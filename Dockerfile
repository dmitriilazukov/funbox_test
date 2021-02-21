FROM python:3.8

WORKDIR /app

COPY Pipfile* ./

RUN pip install pipenv && pipenv install --dev --system

COPY . .

EXPOSE 8000

CMD python manage.py migrate --noinput \
    && python manage.py runserver 0.0.0.0:8000