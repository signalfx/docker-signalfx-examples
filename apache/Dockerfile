FROM phusion/baseimage:0.9.11
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get -y install wget curl apache2 python collectd logrotate python-pip git
RUN service apache2 stop
RUN pip install git+git://github.com/signalfuse/maestro-ng

# Setup Apache
RUN mkdir /var/lock/apache2
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/sf/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
ADD ./apache.conf /etc/apache2/sites-available/
RUN ln -s /etc/apache2/sites-available/apache.conf /etc/apache2/sites-enabled/
RUN mkdir -p /var/log/sf/apache2

EXPOSE 80

# Setup collectd
ADD collectd/collectd.conf /etc/collectd/
RUN mkdir /etc/collectd.d
RUN mkdir /etc/collectd.d/unmanaged_config
RUN mkdir /etc/collectd.d/managed_config
ADD collectd/signalfx_types_db /etc/collectd.d/
ADD collectd/10-apache.conf /etc/collectd.d/unmanaged_config/

# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
ADD logging.ini /opt/collectd-signalfx/
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/collectd-signalfx.conf
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/aggregation.conf

ADD run.py /opt/docker/.docker/
ADD dockercommonpy /opt/docker/.docker/dockercommon.py
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
