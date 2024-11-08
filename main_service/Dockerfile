# Use a slim version of Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire main_service folder into the /app directory in the container
COPY ./main_service /app

# Install dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app will run on
EXPOSE 5000

# Run the server.py file when the container starts
CMD ["python", "server.py"]
