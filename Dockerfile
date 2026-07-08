# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Run the web service on container startup.
# Streamlit listens on port 8501 by default, but Cloud Run passes the $PORT env var.
# We map Streamlit's port to $PORT to ensure Cloud Run can route traffic to it.
CMD ["sh", "-c", "streamlit run frontend2.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
