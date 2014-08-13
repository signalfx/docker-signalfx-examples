import os
import argparse
import subprocess
import re

# Copied from maestro.  Don't require maestro code.
def _to_env_var_name(s):
    """Transliterate a service or container name into the form used for
    environment variable names."""
    return re.sub(r'[^\w]', '_', s).upper()

parser = argparse.ArgumentParser(
    description='Compile/run docker image pretending to be maestro')
parser.add_argument('--expose', default=[], help='Exposed port', action='append')
parser.add_argument('--port', default=[], help='Maestro port', action='append')
parser.add_argument('--service_name', default='test_service')
parser.add_argument('--container_name', default='test_container')
parser.add_argument('user_name')
parser.add_argument('org')
parser.add_argument('password')
parser.add_argument('url')
args = parser.parse_args()

ret = os.system("docker ps | awk '{print $1}' | grep -v CONTAINER | xargs -n1 -r docker kill")
assert ret == 0, "Unable to kill existing docker processes"

ret = os.system("docker build -t testit .")
assert ret == 0, "Unable to build docker image"

docker_cmd = ['docker', 'run']
for e in args.expose:
    if ":" in str(e):
        e = str(e)
    else:
        e = "%d:%d" % (int(e), int(e))
    docker_cmd.extend(['-p', '0.0.0.0:%s' % (e)])

docker_cmd.extend(['-e', 'SERVICE_NAME=%s' % (args.service_name)])
docker_cmd.extend(['-e', 'CONTAINER_NAME=%s' % (args.container_name)])
docker_cmd.extend(['-e', 'SF_AUTH_USERNAME=%s' % (args.user_name)])
docker_cmd.extend(['-e', 'SF_AUTH_ORG=%s' % (args.org)])
docker_cmd.extend(['-e', 'SF_AUTH_PASSWORD=%s' % (args.password)])
docker_cmd.extend(['-e', 'SF_AUTH_URL=%s' % (args.url)])
for p in args.port:
    (expose_name, expose_int) = p.split(":")
    expose_int = int(expose_int)
    docker_cmd.extend(['-e', '%s_%s_%s_INTERNAL_PORT=%d' % (_to_env_var_name(args.service_name), _to_env_var_name(args.container_name), _to_env_var_name(expose_name), expose_int)])

docker_cmd.extend(['-t', 'testit'])
print "Executing %s" % (" ".join(docker_cmd))
proc = subprocess.Popen(docker_cmd)
ret = proc.wait()
assert ret == 0, "Run finished w/ non zero return code"

