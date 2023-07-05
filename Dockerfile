# Use an official Python runtime as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the Flask app code into the container
COPY . .

RUN apt-get update
RUN pip install --upgrade pip
RUN apt-get install -y --no-install-recommends
# Install Apache and configure it
RUN apt-get update && apt-get install -y apache2
RUN apt-get install -y libapache2-mod-wsgi-py3

# Install Apache mods
RUN a2enmod autoindex
RUN a2enmod rewrite
RUN a2enmod headers
RUN a2enmod proxy
RUN a2enmod proxy_http
RUN a2enmod wsgi

# Expose the port that Apache will listen on
EXPOSE 80

COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

# Start Apache with the activated virtual environment
RUN chmod 777 /app/website/database.db
RUN chmod -R 777 /app
RUN chown -R :www-data /app/website/database.db
RUN chown -R :www-data /app
CMD ["apache2ctl", "-D", "FOREGROUND"]
