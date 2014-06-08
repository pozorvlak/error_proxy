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
    def is_path_prefix(self, needle):
        return self.path[0:len(needle)] == needle

    def do_GET(self):
        get_conf = self.config['get']
        matchlen = 0
        match = None
        for path in get_conf:
            if self.is_path_prefix(path) and len(path) > matchlen:
                matchlen = len(path)
                match = path
        if matchlen > 0:
            self.send_error(get_conf[match])
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
            print "Starting server on http://localhost:{}, proxying {}".format(
                    c['port'], c['forward_to'])
        else:
            print "Starting server on http://localhost:{}".format(c['port'])
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
