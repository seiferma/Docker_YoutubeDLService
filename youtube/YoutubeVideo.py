from __future__ import unicode_literals
import cherrypy
import ffmpeg
import re
import youtube_dl
from util.watchdog import WatchDog


class YoutubeVideo(object):

    ID_PATTERN = re.compile('[a-zA-Z0-9_+-]+')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self, videoid):
        if self.ID_PATTERN.match(videoid) is None:
            raise cherrypy.HTTPError(status=400, message='The given video id is invalid.')

        ydl_opts = {
            'simulate': True,
            'quiet': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info('https://www.youtube.com/watch?v=' + videoid, download=False)

    @cherrypy.expose
    def stream(self, videoid, container='mp4'):
        if self.ID_PATTERN.match(videoid) is None:
            raise cherrypy.HTTPError(status=400)
        if container != 'mp4' and container != 'webm':
            raise cherrypy.HTTPError(status=400)

        cherrypy.response.headers['Content-Type'] = 'video/' + container
        return self._yield_streaming_content(videoid, container)
    stream._cp_config = {'response.stream': True}

    def _yield_streaming_content(self, videoid, container_format='mp4'):
        video_container, audio_container, output_args = self._get_output_video_parameters(container_format)
        video_format, audio_format = self._get_youtube_urls(videoid, video_container, audio_container)
        video_input = ffmpeg.input(video_format['url'])
        audio_input = ffmpeg.input(audio_format['url'])
        output = ffmpeg.output(video_input, audio_input, '-', codec='copy', format=container_format, **output_args)
        #print(ffmpeg.compile(output))
        process = ffmpeg.run_async(output, pipe_stdout=True, quiet=True)

        def terminate_process():
            print("Killing ffmpeg process because of timeout.")
            process.kill()
        watchdog = WatchDog(terminate_process, 30)
        watchdog.run()

        def content():
            while True:
                read_data = process.stdout.read(1024)
                yield read_data
                watchdog.process_still_active()
                if len(read_data) == 0 and process.poll() is not None:
                    break
            process.kill()
            print("Terminated ffmpeg")

        return content()

    @staticmethod
    def _get_output_video_parameters(container_format):
        video_container = None
        audio_container = None
        output_args = dict()
        if container_format == 'mp4':
            video_container = 'mp4'
            audio_container = 'm4a'
            output_args = {'movflags': 'frag_keyframe+empty_moov'}
        if container_format == 'webm':
            video_container = 'webm'
            audio_container = 'webm'
        return video_container, audio_container, output_args

    def _get_youtube_urls(self, videoid, video_container='mp4', audio_container='m4a'):
        info_dict = self.index(videoid)
        video_format = None
        audio_format = None

        for format in info_dict['formats']:
            if format['ext'] == video_container and format['vcodec'] != 'none':
                if video_format is None or int(video_format['width']) < int(format['width']):
                    video_format = format
            if format['ext'] == audio_container and format['acodec'] != 'none':
                if audio_format is None or int(audio_format['abr']) < int(format['abr']):
                    audio_format = format

        return video_format, audio_format
