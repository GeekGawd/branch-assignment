# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py makemigrations

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "branch.asgi:application"]