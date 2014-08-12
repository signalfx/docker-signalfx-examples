FROM quay.io/signalfuse/maestro-base:14.04-0.1.8.1
MAINTAINER Jack Lindamood <jack@signalfuse.com>

RUN apt-get update
RUN apt-get install -y apache2 curl python collectd logrotate

RUN mkdir /var/lock/apache2
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/sf/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

EXPOSE 83

ENV DEBIAN_FRONTEND noninteractive

# Setup collectd
ADD ../nginx_php_mysql_statsd/collectd.conf /etc/collectd/
RUN mkdir /etc/collectd.d
RUN mkdir /etc/collectd.d/unmanaged_config
RUN mkdir /etc/collectd.d/managed_config
ADD ../nginx_php_mysql_statsd/signalfx_types_db /etc/collectd.d/
ADD image_logrotate.conf /etc/logrotate.d/
ADD apache-collectd.conf /etc/collectd.d/managed_config/

# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/collectd-signalfx.conf
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/aggregation.conf
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/aggregation.conf

ADD ./apache.conf /etc/apache2/sites-available/
RUN ln -s /etc/apache2/sites-available/apache.conf /etc/apache2/sites-enabled/

RUN mkdir -p /var/log/sf/apache2
ADD run.py /opt/docker/.docker/
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
