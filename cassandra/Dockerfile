FROM quay.io/signalfuse/maestro-base:14.04-0.1.8.1
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

RUN sudo apt-get update
RUN sudo apt-get -y install wget curl python collectd logrotate

# Setup private keys https://wiki.apache.org/cassandra/DebianPackaging
RUN echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
RUN curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -

# Then install
RUN sudo apt-get update
RUN sudo apt-get -y install dsc20
RUN sudo service cassandra stop
RUN sudo rm -rf /var/lib/cassandra/data/system/*
RUN sed -i -e "s/^rpc_address.*/rpc_address: 0.0.0.0/" /etc/cassandra/cassandra.yaml
RUN pip install cassandra-driver

EXPOSE 9160
ADD run.py /opt/docker/.docker/
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
