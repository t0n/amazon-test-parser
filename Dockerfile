# Use an official Python runtime as a parent image
FROM python:3.5.4-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Update all and install additional tools
RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends apt-utils && \
  apt-get install -yqq apt-transport-https && \
  apt-get install -y wget \
    ca-certificates \
    bzip2 \
    vim \
    libfontconfig

# Install Node 6.*
RUN \
  echo "deb https://deb.nodesource.com/node_6.x jessie main" > /etc/apt/sources.list.d/nodesource.list && \
  wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  apt-get update && \
  apt-get install -yqq nodejs && \
  rm -rf /var/lib/apt/lists/*

# Install PhantomJS
RUN \
    npm install -g phantomjs-prebuilt

# Install any needed packages specified in requirements.txt
RUN \
    pip install -r requirements.txt
