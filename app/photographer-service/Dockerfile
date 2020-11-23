FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY . .
ENV MODULE_NAME=photographer_service
RUN pip3 install --proxy http://proxy.rennes.enst-bretagne.fr:3128 --no-cache-dir --trusted-host pypi.python.org mongoengine requests



