FROM python:slim

WORKDIR /app

COPY . .

RUN python3 -m venv venv
RUN . ./venv/bin/activate
RUN mkdir log
RUN python3 -m pip install -r req.txt

CMD ["python", "main.py"]