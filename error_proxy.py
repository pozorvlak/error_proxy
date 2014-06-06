#!/usr/bin/env python

import sys
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urljoin
from urllib import URLopener
from threading import Thread

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

if __name__ == "__main__":
    if sys.argv[1:]:
        config_file = sys.argv[1]
    else:
        config_file = "Proxyfile"
    with open(config_file) as fh:
        config = json.load(fh)
    httpds = []
    for i, c in enumerate(config):
        HandlerClass = type('ProxyHandler{}'.format(i),
                (ErrorHTTPRequestHandler,),
                { 'config': c })
        httpd = HTTPServer(("localhost", c['port']), HandlerClass)
        httpds.append(httpd)
        Thread(target=httpd.serve_forever).start()
    for h in httpds:
        h.shutdown()
