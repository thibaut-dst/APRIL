# Use an official Python image
FROM python:3.9-slim

# Define the working directory
WORKDIR /app

# Copy files to image
COPY build/requirements.txt build/requirements.txt
COPY app.py app.py
COPY functions/ functions/
COPY templates/ templates/
COPY routes/ routes/
COPY static/ static/
COPY data/ data/

RUN pip install --no-cache-dir -r build/requirements.txt
RUN python3 -m spacy download fr_core_news_lg
RUN apt-get update && apt-get install -y iputils-ping
RUN touch pipeline.log

# Expose the Flask API port
EXPOSE 5000

# Launch Flask in development mode
CMD ["python", "app.py"]
