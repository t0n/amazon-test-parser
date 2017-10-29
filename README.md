# amazon-test-parser

Test project to parse search results on Amazon.com



## Requirements

- NodeJS, npm
- Python3
- virtualenv


or Docker



## Installation

### Linux

Run ./install.sh script (will ask for sudo password to install phantomjs globally)

### MacOS 

(TODO)

### Docker

docker run antonkoba/amazon-test-parser:v1



## Running

### Linux

Run ./run.sh <Your Search Query>

### MacOS

(TODO)

### Docker

Run:

docker run -it amazon-test-parser /bin/bash

or

docker run -it antonkoba/amazon-test-parser:v1 /bin/bash



Inside running docker container:

vi settings.py

python parse.py <Your Search Query>

