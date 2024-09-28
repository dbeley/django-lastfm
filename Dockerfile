# Use a slim version of the Python image to reduce size
FROM python:3-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /code

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install only the packages necessary for your application
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the application port
EXPOSE 8000

# Command to run your application (e.g., using Django's runserver)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
