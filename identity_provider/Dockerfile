FROM python:3.8-buster as build

WORKDIR /home/server

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM python:3.8-slim as server

WORKDIR /home/server

COPY --from=build /root/.cache /root/.cache

RUN apt-get update && apt-get install -y libpq5 && apt-get clean

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY *.py ./

CMD ["python", "api.py"]
