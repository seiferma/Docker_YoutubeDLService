from __future__ import unicode_literals
import cherrypy
from youtube.Youtube import Youtube


class Root(object):

    def __init__(self):
        self.youtube = Youtube()


if __name__ == '__main__':
    cherrypy.config.update({'environment': 'production'})
    cherrypy.config.update({'log.screen': True,
                            'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(Root(), '/')