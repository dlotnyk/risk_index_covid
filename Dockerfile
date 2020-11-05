FROM python:3.7.9-stretch

RUN apt-get update && \
  apt-get install -y software-properties-common tcl-dev tk-dev python-tk python3-tk
RUN apt-get update

# update pip
RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install wheel matplotlib requests flask
ENTRYPOINT ["python3"]