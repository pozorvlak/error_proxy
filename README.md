error_proxy
===========

Suppose

 - you're doing a manual test and/or demo of some code
 - that uses a web service
 - you want to test your ability to handle third-party errors
 - but stubbing out the *whole* service makes your tests a pain to set up?
 
This program is designed for that situation. Create a small JSON file containing a list of site configurations; for each site you want to proxy, the configuration object should specify

 - what port you want to start the server on
 - what site you want requests to be forwarded to
 - what endpoints you want to stub out, and what error code to return in each case
 
Then run `error_proxy.py [config file]`. There's a hopefully self-explanatory configuration file in `Proxyfile.example`.
