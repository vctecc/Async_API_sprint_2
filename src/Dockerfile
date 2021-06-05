FROM python:3.9.1-slim

EXPOSE 8000

WORKDIR /opt/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . src/

ENTRYPOINT ["python", "/opt/app/src/main.py"]