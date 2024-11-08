# Use a slim version of Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire product_service folder to /app inside the container
COPY ./product_service /app

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app will run on
EXPOSE 5002

# Run the product_service.py when the container starts
CMD ["python", "product_service.py"]
