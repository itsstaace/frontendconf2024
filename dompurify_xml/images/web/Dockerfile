FROM python:3.9

WORKDIR /app

COPY src/ ./

RUN pip install flask==3.0.3 bcrypt==4.1.2

CMD ["python", "app.py"]
