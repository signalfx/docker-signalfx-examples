FROM phusion/baseimage:0.9.11
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get update
RUN apt-get -y upgrade

RUN add-apt-repository ppa:webupd8team/java
RUN apt-get update

# Yes, we accept the license oracle!!! (ugh non interactive installs ...)
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections

RUN apt-get install -y oracle-java7-installer

RUN sudo apt-get -y install wget curl python collectd logrotate build-essential python-dev libev4 libev-dev python-pip git mlocate
RUN pip install git+git://github.com/signalfuse/maestro-ng
RUN pip install blist

# Setup private keys https://wiki.apache.org/cassandra/DebianPackaging
RUN echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
RUN curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -

# Then install
RUN apt-get update
RUN apt-get -y install dsc20
RUN service cassandra stop
RUN rm -rf /var/lib/cassandra/data/system/*
# Allow me to connect into this instance
RUN sed -i -e "s/^rpc_address.*/rpc_address: 0.0.0.0/" /etc/cassandra/cassandra.yaml
RUN cd /lib64 && ln -s /usr/lib/jvm/java-7-oracle/jre/lib/amd64/server/libjvm.so
# http://www.willdurness.com/collectinggraphing-information-on-neo4j-via-collectd-and-graphite/
# Seems easiest to just find a comment that's kinda where I want this line, and replace that comment with what I need
# The basic problem is collectd is compiled thinking openjdk, but i'm using oracle, so I need to
# point it to the correct location
RUN sed -i -e "s|^# Gracefully exit if the package has been removed.|export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/lib/jvm/java-7-oracle/jre/lib/amd64/server|" /etc/init.d/collectd
RUN pip install cassandra-driver

# Setup collectd
ADD collectd/collectd.conf /etc/collectd/
RUN mkdir /etc/collectd.d
RUN mkdir /etc/collectd.d/unmanaged_config
RUN mkdir /etc/collectd.d/managed_config
ADD collectd/signalfx_types_db /etc/collectd.d/
ADD collectd/10-jmx.conf /etc/collectd.d/unmanaged_config/
ADD collectd/20-cassandra.conf /etc/collectd.d/unmanaged_config/

# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
ADD logging.ini /opt/collectd-signalfx/
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/collectd-signalfx.conf
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/aggregation.conf

EXPOSE 9160
ADD run.py /opt/docker/.docker/
ADD dockercommonpy /opt/docker/.docker/dockercommon.py
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
