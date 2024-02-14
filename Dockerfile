FROM node:20.11.0-alpine as build

WORKDIR /app
COPY package.json /app
RUN npm install

FROM python:3.12

COPY . app
WORKDIR /app

COPY --from=build /app /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8080
ENV PORT 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]