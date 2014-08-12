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

ADD ./apache.conf /etc/apache2/sites-available/
RUN ln -s /etc/apache2/sites-available/apache.conf /etc/apache2/sites-enabled/

RUN mkdir -p /var/log/sf/apache2
ADD run.py /opt/docker/.docker/
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
