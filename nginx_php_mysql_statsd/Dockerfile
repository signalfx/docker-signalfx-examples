# Dockerfile for a third party nginx/mysql/php/statsd stack

FROM quay.io/signalfuse/maestro-base:14.04-0.1.8.1
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
# Upgrade currently unable to run?
#RUN apt-get -y upgrade

# Install all apt-get utils
RUN apt-get -y install curl python mysql-client mysql-server nginx php5-fpm php5-mysql collectd python logrotate

RUN service nginx stop

# Setup PHP install
ADD info.php /usr/share/nginx/html/
ADD select.php /usr/share/nginx/html/
ADD delete.php /usr/share/nginx/html/
ADD insert.php /usr/share/nginx/html/
ADD statsd.php /usr/share/nginx/html/
ADD statsd.ini /usr/share/nginx/html/

# Setup nginx config
ADD nginx.conf /etc/nginx/
#RUN mkdir /var/log/sf && nginx -t File does not start off valid.  has %%%__%%%
EXPOSE 81

# Setup collectd
ADD collectd.conf /etc/collectd/
RUN mkdir /etc/collectd.d
RUN mkdir /etc/collectd.d/unmanaged_config
RUN mkdir /etc/collectd.d/managed_config
ADD signalfx_types_db /etc/collectd.d/
ADD 10-innodb.conf /etc/collectd.d/unmanaged_config/
ADD 10-mysql.conf /etc/collectd.d/unmanaged_config/
ADD 10-nginx.conf /etc/collectd.d/unmanaged_config/
ADD 10-statsd.conf /etc/collectd.d/unmanaged_config/
ADD image_logrotate.conf /etc/logrotate.d/

RUN cd /opt && git clone https://github.com/marksteele/collectd-plugins.git /opt/collectd-plugins

# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/collectd-signalfx.conf

# Setup run script to start the server
ADD run.py /opt/docker/.docker/
VOLUME /var/log/sf/

CMD ["python", "/opt/docker/.docker/run.py"]
