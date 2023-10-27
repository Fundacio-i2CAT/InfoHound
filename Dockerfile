# Use an official Python runtime as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install exiftool and maigret
RUN apt-get update && apt-get install -y exiftool

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file to the container
COPY requirements.txt /code/

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the container
COPY . /code/

# Expose the Django development server port
EXPOSE 8000

# Start the Django development server
CMD python manage.py runserver 0.0.0.0:8000