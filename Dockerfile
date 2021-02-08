FROM dyne/devuan:chimaera

WORKDIR /app

RUN apt-get update -y -q \
	&& apt-get install -y -q python3-venv virtualenv \
    && apt-get clean -y -q

COPY . .

RUN virtualenv -p /usr/bin/python3 venv \
	&& . ./venv/bin/activate \
	&& pip3 install -r requirements.txt

CMD . ./venv/bin/activate && python3 main.py

