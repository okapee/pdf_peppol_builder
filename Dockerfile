# pythonのバージョンは任意
FROM python:3.10

WORKDIR /usr/src/app
ENV FLASK_APP=app

COPY /app/requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]