FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
<<<<<<< HEAD
    PYTHONUNBUFFERED=1
=======
  PYTHONUNBUFFERED=1
>>>>>>> 9dd27fe99b95c6cc9874d91500679bbda8a60c97

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]