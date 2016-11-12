#!/home3/unmoldab/venvs/flask/bin/python

from flipflop import WSGIServer
from ip import app as application

WSGIServer(application).run()

