from __future__ import unicode_literals
import cherrypy
from .YoutubeVideos import YoutubeVideos


class Youtube(object):

    def __init__(self):
        self.video = YoutubeVideos()

    def _cp_dispatch(self, vpath):
        if len(vpath) > 1:
            subelement = vpath.pop()
            if subelement == 'video':
                cherrypy.request.params['videoid'] = vpath.pop(0)
                return self.video

            return self

        return vpath

