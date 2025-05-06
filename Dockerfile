# ---- Base image ----
    FROM python:3.11-slim

    # Set working directory
    WORKDIR /backend
    
    # Install backend dependencies
    COPY backend/requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy backend source code
    COPY backend/ .
    
    # Expose FastAPI port
    EXPOSE 8000
    
    # Run FastAPI with uvicorn
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    