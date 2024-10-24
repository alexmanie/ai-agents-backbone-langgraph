FROM python:3.9-slim

WORKDIR /usr/src/app

COPY frontend/. .

RUN pip3 install -r requirements.txt

EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "app.py"]