FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY cards cards
COPY bot.py bot.py
COPY watcher.py watcher.py

ENTRYPOINT ["python"]
CMD ["bot.py"]