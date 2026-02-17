FROM python:3.11-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements_chatbot.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_chatbot.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs config

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (if needed for web interface later)
EXPOSE 8080

# Run the chatbot
CMD ["python", "chatbot/main_app.py"]