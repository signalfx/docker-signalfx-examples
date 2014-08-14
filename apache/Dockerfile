FROM phusion/baseimage:0.9.11
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

# Clean/refresh apt-get
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get update
RUN apt-get -y upgrade

# Install dependencies
RUN apt-get -y install wget curl apache2 python collectd python-pip git
RUN service apache2 stop
RUN service collectd stop
RUN pip install git+git://github.com/signalfuse/maestro-ng

# Setup Apache
RUN mkdir /var/lock/apache2
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/sf/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
ADD apache.conf /etc/apache2/sites-available/
RUN ln -s /etc/apache2/sites-available/apache.conf /etc/apache2/sites-enabled/
RUN mkdir -p /var/log/sf/apache2
EXPOSE 80

# Setup collectd
RUN mkdir -p /etc/collectd.d/managed_config
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/collectd.conf           /etc/collectd/
RUN sed -i -e 's#FQDNLookup true#Hostname "%%%HOSTNAME%%%"#'  /etc/collectd/collectd.conf
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/signalfx_types_db       /etc/collectd.d/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-apache.conf          /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-aggregation-cpu.conf /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-signalfx.conf        /etc/collectd.d/managed_config/
RUN sed -i 's/APIToken "%%%API_TOKEN%%%"/APIToken "%%%API_TOKEN%%%"\n    url "%%%API_HOST%%%"/'         /etc/collectd.d/managed_config/10-signalfx.conf

# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
RUN sed -i -e "s#/var/log/collectd_signalfx.log#/var/log/sf/collectd_signalfx.log#" /opt/collectd-signalfx/logging.ini
RUN sed -i -e "s#/var/log/collectd_signalfx.log#/var/log/sf/collectd_signalfx.log#" /opt/collectd-signalfx/logging.ini


# Add run command
ADD run.py /opt/docker/.docker/
ADD dockercommonpy /opt/docker/.docker/dockercommon.py
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
