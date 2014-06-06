#!/usr/bin/env python

import sys
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class ErrorHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(self.config['get_response'])

if sys.argv[1:]:
    config_file = sys.argv[1:]
else:
    config_file = "Proxyfile"
with open(config_file) as c:
    config = json.load(c)
ErrorHTTPRequestHandler.config = config
httpd = HTTPServer(("localhost", config['port']), ErrorHTTPRequestHandler)
httpd.serve_forever()
