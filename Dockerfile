# pythonのバージョンは任意
FROM python:3.8

WORKDIR /usr/src/app
ENV FLASK_APP=app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential lsof && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y

EXPOSE 5000

COPY . .

CMD ["flask", "run"]