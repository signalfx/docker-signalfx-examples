FROM phusion/baseimage:0.9.11
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

# Clean/refresh apt-get
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get update
RUN apt-get -y upgrade

# Install Oracle Java 7
RUN add-apt-repository ppa:webupd8team/java
RUN apt-get update
# Yes, we accept the license oracle!!! (ugh non interactive installs ...)
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
RUN apt-get install -y oracle-java7-installer

# Install dependencies
RUN sudo apt-get -y install curl python collectd build-essential python-dev libev4 libev-dev python-pip git
RUN pip install git+git://github.com/signalfuse/maestro-ng
RUN pip install blist

# Install cassandra
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
RUN pip install cassandra-driver
EXPOSE 9160

# Setup collectd
RUN mkdir -p /etc/collectd.d/managed_config
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/collectd.conf           /etc/collectd/
RUN sed -i -e 's#FQDNLookup true#Hostname "%%%HOSTNAME%%%"#'  /etc/collectd/collectd.conf
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/signalfx_types_db       /etc/collectd.d/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-aggregation-cpu.conf /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-jmx.conf             /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/20-cassandra.conf       /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-signalfx.conf        /etc/collectd.d/managed_config/
RUN sed -i 's/APIToken "%%%API_TOKEN%%%"/APIToken "%%%API_TOKEN%%%"\n    url "%%%API_HOST%%%"/'         /etc/collectd.d/managed_config/10-signalfx.conf


# Setup java.so plugin
RUN cd /lib64 && ln -s /usr/lib/jvm/java-7-oracle/jre/lib/amd64/server/libjvm.so
# https://bugzilla.redhat.com/show_bug.cgi?id=1212151
# Seems easiest to just find a comment that's kinda where I want this line, and replace that comment with what I need
# The basic problem is collectd is compiled thinking openjdk, but i'm using oracle, so I need to
# point it to the correct location
RUN sed -i -e "s|^# Gracefully exit if the package has been removed.|export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/lib/jvm/java-7-oracle/jre/lib/amd64/server|" /etc/init.d/collectd


# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
RUN sed -i -e "s#/var/log/collectd_signalfx.log#/var/log/sf/collectd_signalfx.log#" /opt/collectd-signalfx/logging.ini

# Add run command
ADD run.py /opt/docker/.docker/
ADD dockercommonpy /opt/docker/.docker/dockercommon.py
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
