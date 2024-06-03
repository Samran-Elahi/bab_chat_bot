# Use an official Python runtime as a parent image
FROM python:3.11.5-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy and set environment variables
COPY .env /app/.env

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Start the FastAPI application
CMD ["uvicorn", "BaB_chatbot:app", "--host", "0.0.0.0", "--port", "3000"]
