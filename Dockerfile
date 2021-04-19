FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY bot/ ./bot

ENTRYPOINT ["python"]
CMD ["bot/bot.py"]