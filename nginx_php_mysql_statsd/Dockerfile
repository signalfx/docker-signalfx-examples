FROM phusion/baseimage:0.9.11
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

# Clean/refresh apt-get
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get update
RUN apt-get -y upgrade

# Install dependencies
RUN apt-get -y install curl python mysql-client mysql-server nginx php5-fpm php5-mysql collectd python logrotate python-pip git
RUN pip install git+git://github.com/signalfuse/maestro-ng

# Stop existing services
RUN service nginx stop
RUN service collectd stop

# Setup PHP
ADD php/info.php /usr/share/nginx/html/
ADD php/select.php /usr/share/nginx/html/
ADD php/delete.php /usr/share/nginx/html/
ADD php/insert.php /usr/share/nginx/html/
ADD php/statsd.php /usr/share/nginx/html/
ADD statsd.ini /usr/share/nginx/html/

# Setup nginx
ADD nginx.conf /etc/nginx/
RUN mkdir /var/log/sf && nginx -t
EXPOSE 80

# Setup collectd
RUN mkdir -p /etc/collectd.d/managed_config
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/collectd.conf           /etc/collectd/
RUN sed -i -e 's#FQDNLookup true#Hostname "%%%HOSTNAME%%%"#'  /etc/collectd/collectd.conf
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/signalfx_types_db       /etc/collectd.d/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-aggregation-cpu.conf /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-nginx.conf           /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-innodb.conf          /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-statsd.conf          /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-mysql.conf           /etc/collectd.d/managed_config/
ADD https://raw.githubusercontent.com/signalfx/signalfx-collectd-configs/master/10-signalfx.conf        /etc/collectd.d/managed_config/
RUN sed -i 's/APIToken "%%%API_TOKEN%%%"/APIToken "%%%API_TOKEN%%%"\n    url "%%%API_HOST%%%"/'         /etc/collectd.d/managed_config/10-signalfx.conf

# Setup logrotate
ADD image_logrotate.conf /etc/logrotate.d/

# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
RUN sed -i -e "s#/var/log/collectd_signalfx.log#/var/log/sf/collectd_signalfx.log#" /opt/collectd-signalfx/logging.ini

# Setup another collectd plugin
RUN cd /opt && git clone https://github.com/marksteele/collectd-plugins.git /opt/collectd-plugins

# Add run command
ADD run.py /opt/docker/.docker/
ADD dockercommonpy /opt/docker/.docker/dockercommon.py
VOLUME /var/log/sf/
USER root
CMD ["python", "/opt/docker/.docker/run.py"]
