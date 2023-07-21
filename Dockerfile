# pythonのバージョンは任意
FROM python

WORKDIR /usr/src/app
ENV FLASK_APP=app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]