# ---- Base image ----
    FROM python:3.11

    # Set working directory
    WORKDIR /app
    
    # Install backend dependencies
    COPY backend/requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY backend/ ./backend

    COPY frontend/ ./backend/static
    
    # Expose FastAPI port
    EXPOSE 8000
    
    # Move into backend to run the app
    WORKDIR /app/backend
    
    # Run FastAPI with uvicorn
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    