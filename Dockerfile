FROM python:3.9.9

RUN mkdir /TaskSaas -p

WORKDIR /TaskSaas

ADD ./requirements.txt /TaskSaas
ADD ./ /TaskSaas

RUN cd /TaskSaas
RUN pip install -r requirements.txt


CMD ["python","manage.py","runserver","0:3000"]