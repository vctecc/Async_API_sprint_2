FROM python:3.9.1-slim

EXPOSE 8000

WORKDIR /opt/app

COPY src/requirements.txt src/requirements.txt
RUN pip install -r ./src/requirements.txt

COPY . .

ENTRYPOINT ["python", "/opt/app/src/main.py"]