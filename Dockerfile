FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install flask flask-cors
EXPOSE 8000
CMD ["python", "app.py"]
