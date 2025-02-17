# Use the official Python image from the Docker Hub
FROM python:3.12.0-slim-bookworm

# Set environment variables
ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1
ENV APP=/app

# Set the working directory
WORKDIR $APP

# Copy the requirements file into the container
COPY requirements.txt $APP

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . $APP

# Expose the port the app runs on
EXPOSE 8000

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]

# Command to run the application
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangoproj.wsgi"]