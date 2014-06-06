#!/usr/bin/env python

import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class ErrorHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(420)

if sys.argv[1:]:
    port = sys.argv[1:]
else:
    port = 8000
httpd = HTTPServer(("localhost", port), ErrorHTTPRequestHandler)
httpd.serve_forever()
