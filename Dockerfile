FROM python:3.9.9

RUN mkdir /TaskSaas_Dck -p

WORKDIR /TaskSaas_Dck

#ADD ./requirements.txt /TaskSaas
ADD ./ /TaskSaas_Dck

RUN cd /TaskSaas_Dck
RUN pip install -r requirements.txt



CMD ["python","manage.py","runserver","0:3000"]