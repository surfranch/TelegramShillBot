FROM python:3.10-alpine

RUN apk --no-cache add build-base

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY images/ /app/images/
COPY tg_shill_bot.py settings.yml /app/

CMD ["python", "-u", "tg_shill_bot.py"]
