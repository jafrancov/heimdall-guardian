FROM python:latest
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV DB_PASSWORD=Sup3rS3cretPassw0rd9x
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
