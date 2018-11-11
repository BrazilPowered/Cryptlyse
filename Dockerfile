FROM alpine:3.8
RUN apk update && apk upgrade && apk add python3 \
&& pip3 install --upgrade pip
ENV FLASK_APP=cryptlyse.py
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["cryptlyse.py"]