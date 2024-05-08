# Use the official Python image as a base
# Use a specific Python version
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and requirements file into the container
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir \
    pika \
    lxml \
    python-dotenv

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


# Run the Python script when the container starts
CMD [ "supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf" ]