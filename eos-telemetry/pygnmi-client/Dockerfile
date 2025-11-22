FROM python:3.12
WORKDIR /pygnmi-client

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-logstash

COPY pygnmi_client.py /pygnmi-client
CMD ["python", "./pygnmi_client.py"]
