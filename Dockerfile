FROM python:3.12

COPY . quayside
WORKDIR /quayside

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]