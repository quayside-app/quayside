FROM python:3.12

COPY . quayside
WORKDIR /quayside

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

#RUN npm run build


EXPOSE 8080
ENV PORT 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]