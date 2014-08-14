FROM phusion/baseimage:0.9.11
MAINTAINER Jack Lindamood <jack@signalfuse.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get update
RUN apt-get -y upgrade

# Install all apt-get utils
RUN apt-get -y install curl python mysql-client mysql-server nginx php5-fpm php5-mysql collectd python logrotate python-pip git
RUN pip install git+git://github.com/signalfuse/maestro-ng

RUN service nginx stop
RUN service collectd stop

# Setup PHP install
ADD php/info.php /usr/share/nginx/html/
ADD php/select.php /usr/share/nginx/html/
ADD php/delete.php /usr/share/nginx/html/
ADD php/insert.php /usr/share/nginx/html/
ADD php/statsd.php /usr/share/nginx/html/
ADD statsd.ini /usr/share/nginx/html/

# Setup nginx config
ADD nginx.conf /etc/nginx/
RUN mkdir /var/log/sf && nginx -t
EXPOSE 80

# Setup collectd
ADD collectd/collectd.conf /etc/collectd/
RUN mkdir /etc/collectd.d
RUN mkdir /etc/collectd.d/unmanaged_config
RUN mkdir /etc/collectd.d/managed_config
ADD collectd/signalfx_types_db /etc/collectd.d/
ADD collectd/10-innodb.conf /etc/collectd.d/unmanaged_config/
ADD collectd/10-mysql.conf /etc/collectd.d/unmanaged_config/
ADD collectd/10-nginx.conf /etc/collectd.d/unmanaged_config/
ADD collectd/10-statsd.conf /etc/collectd.d/unmanaged_config/
ADD image_logrotate.conf /etc/logrotate.d/

# Install our collectd plugin
RUN cd /opt && git clone https://github.com/signalfx/collectd-signalfx.git /opt/collectd-signalfx
ADD logging.ini /opt/collectd-signalfx/
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/collectd-signalfx.conf
RUN cd /etc/collectd.d/unmanaged_config/ && ln -s /opt/collectd-signalfx/aggregation.conf

# Setup another collectd plugin
RUN cd /opt && git clone https://github.com/marksteele/collectd-plugins.git /opt/collectd-plugins

# Setup run script to start the server
ADD run.py /opt/docker/.docker/
#### Docker does not allow symlinks :(
ADD dockercommonpy /opt/docker/.docker/dockercommon.py
VOLUME /var/log/sf/

CMD ["python", "/opt/docker/.docker/run.py"]
