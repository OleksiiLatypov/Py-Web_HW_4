FROM python:3.10-alpine

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5050


VOLUME ["/storage/data.json"]

ENTRYPOINT ["python", "main.py"]