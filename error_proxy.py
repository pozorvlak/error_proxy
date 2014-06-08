#!/usr/bin/env python

import sys
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urljoin
from urllib import URLopener
from threading import Thread
import signal
import os
import time

class ErrorHTTPRequestHandler(BaseHTTPRequestHandler, object):
    def do_GET(self):
        get_conf = self.config['get']
        if self.path in get_conf:
            self.send_error(get_conf[self.path])
        elif "forward_to" in self.config:
            url = urljoin(self.config['forward_to'], self.path)
            self.log_request()
            self.log_message("Forwarding to {}".format(url))
            o = URLopener().open(url)
            self.wfile.write(o.read())
            o.close()
        else:
            self.send_error(get_conf['*'])

httpds = []

def kill_all_servers():
    for h in httpds:
        print "killing server on port {}".format(h.server_port)
        h.shutdown()
    # Garbage-collect all servers, to prevent port conflicts with new ones
    for i in xrange(len(httpds)):
        httpds.pop()

def shutdown(*args):
    kill_all_servers()
    sys.exit(0)

def start_servers(config_file):
    with open(config_file) as fh:
        config = json.load(fh)
    for i, c in enumerate(config):
        HandlerClass = type('ProxyHandler{}'.format(i),
                (ErrorHTTPRequestHandler,),
                { 'config': c })
        if 'forward_to' in c:
            print "Starting server on port {}, proxying {}".format(
                    c['port'], c['forward_to'])
        else:
            print "Starting server on port {}".format(c['port'])
        httpd = HTTPServer(("localhost", c['port']), HandlerClass)
        httpds.append(httpd)
        Thread(target=httpd.serve_forever).start()

if __name__ == "__main__":
    if sys.argv[1:]:
        config_file = sys.argv[1]
    else:
        config_file = "Proxyfile"
    config_mtime = os.stat(config_file).st_mtime
    start_servers(config_file)
    signal.signal(signal.SIGINT, shutdown)
    while 1:
        time.sleep(1)
        new_config_mtime = os.stat(config_file).st_mtime
        if new_config_mtime != config_mtime:
            config_mtime = new_config_mtime
            print "Detected change to {}".format(config_file)
            kill_all_servers()
            start_servers(config_file)
