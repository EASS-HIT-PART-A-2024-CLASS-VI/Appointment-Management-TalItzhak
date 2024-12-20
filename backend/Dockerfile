FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# הרצה אוטומטית של יצירת מסד הנתונים
RUN python create_db.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
