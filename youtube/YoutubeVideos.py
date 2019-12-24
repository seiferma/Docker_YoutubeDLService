from __future__ import unicode_literals
import cherrypy
from .YoutubeVideo import YoutubeVideo


class YoutubeVideos(object):

    def __init__(self):
        self.youtube_video = YoutubeVideo()

    def _cp_dispatch(self, vpath):
        if len(vpath) > 0:
            cherrypy.request.params['videoid'] = vpath.pop(0)
            return self.youtube_video
        return vpath
