FROM python:3.8-slim as server

WORKDIR /home/server

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY *.py ./

CMD ["python", "api.py"]
