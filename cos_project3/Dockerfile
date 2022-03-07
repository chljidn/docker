FROM continuumio/miniconda3

RUN apt-get -y update
RUN apt-get -y install vim

RUN mkdir /srv/docker
ADD . /srv/docker

# environment.yaml을 통해서 설치할 때, env 같이 쓸 것
RUN conda env create -f /srv/docker/environment.yaml

# 환경변수 설정
ENV PATH /opt/conda/envs/cos_project3/bin:$PATH
ENV /bin/bash -c cos_project3
WORKDIR /srv/docker



RUN pip install --upgrade pip
RUN pip install -r requirements.txt

