FROM python:3.14-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY backend/app ./backend/app
RUN mkdir -p /app/data && chown -R appuser:appuser /app
USER appuser
ENV FINQUANT_DATA_DIR=/app/data
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
