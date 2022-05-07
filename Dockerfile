FROM python:3.10

WORKDIR /app

RUN apt-get update -y -q


# adding chrome to source list
# https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md#running-puppeteer-in-docker
RUN  apt-get install -y wget gnupg \
	&& wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
	gpg -q --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/78BD65473CB3BD13.gpg --import \
	&& chmod 644 /etc/apt/trusted.gpg.d/78BD65473CB3BD13.gpg \
	&& sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

# installing chrome binary and additional fonts 
RUN apt-get update \
	&& apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 \
	--no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*

ENV GOOGLE_CHROME_SHIM=/usr/bin/google-chrome \
	# pip
	PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1

RUN pip install poetry

# copy the source into the virtual space
COPY . /app/

# install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-ansi

# run the program
CMD ["python", "."]
