#!/usr/bin/env python

import sys
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urljoin
from urllib import URLopener

class ErrorHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print self.path
        get_conf = self.config['get']
        if self.path in get_conf:
            self.send_error(get_conf[self.path])
        elif "forward_to" in self.config:
            url = urljoin(self.config['forward_to'], self.path)
            o = URLopener().open(url)
            self.wfile.write(o.read())
            o.close()
        else:
            self.send_error(get_conf['*'])

if sys.argv[1:]:
    config_file = sys.argv[1:]
else:
    config_file = "Proxyfile"
with open(config_file) as c:
    config = json.load(c)
ErrorHTTPRequestHandler.config = config
httpd = HTTPServer(("localhost", config['port']), ErrorHTTPRequestHandler)
httpd.serve_forever()
