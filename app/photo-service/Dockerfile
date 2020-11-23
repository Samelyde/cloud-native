FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY . .
ENV MODULE_NAME=photo_service
RUN python3 -m pip install --proxy http://proxy.rennes.enst-bretagne.fr:3128 --upgrade pip
RUN python3 -m pip install --proxy http://proxy.rennes.enst-bretagne.fr:3128 --upgrade Pillow
RUN pip3 install --proxy http://proxy.rennes.enst-bretagne.fr:3128 --trusted-host pypi.python.org mongoengine requests requests-toolbelt flask python-multipart protobuf google grpcio grpcio-tools
EXPOSE 80