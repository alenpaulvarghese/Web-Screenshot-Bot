FROM  mcr.microsoft.com/playwright/python:v1.51.0-jammy

WORKDIR /app

RUN apt-get update -y -q

# installing chrome binary and additional fonts
RUN apt-get install -y fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 gcc python3-dev \
	--no-install-recommends

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# copy the source into the virtual space
COPY . /app/

# install dependencies
RUN pip install -r requirements.txt

# Remove build dependencies
RUN apt remove gcc python3-dev -y && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# run the program
CMD ["python", "."]
