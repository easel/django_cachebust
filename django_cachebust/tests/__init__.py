import logging
import os
import warnings

from django.http import HttpRequest, HttpResponse
from unittest import TestCase

from django_cachebust import settings, logger
from django_cachebust.middleware import CacheBustMiddleware

warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)

class CBTestCase(TestCase):
    """base class for cachebust tests"""

    def setUp(self):
        self.cb = CacheBustMiddleware()
        

class CacheBustMiddlewareTest(CBTestCase):
    def setUp(self):
        """set up some content to practice on in self.content"""
        CBTestCase.setUp(self)

        self.workdir = os.tmpnam()
        os.mkdir(self.workdir)
        os.mkdir(os.path.join(self.workdir, 'folder'))
        for f in ('favicon.ico',):
            fh = file(os.path.join(self.workdir, f), 'w')
            fh.write('testfile')
        settings.STATIC_URL = 'http://static.example.com/'
        logger.debug(settings.STATIC_URL)
        settings.STATIC_ROOT = self.workdir
        logger.debug(settings.STATIC_ROOT)
        settings.MEDIA_URL = settings.STATIC_URL + 'media/' 
        logger.debug(settings.MEDIA_URL)
        settings.CACHEBUST_STATIC_URL = 'true'
        settings.CACHEBUST_STATIC_LOCAL_URL = 'true'
        settings.CACHEBUST_MEDIA_URL = 'true'
        self.request = HttpRequest()
        self.response = HttpResponse()
        self.response.content = """
        <html>
        <head>
        <link src="%(STATIC_URL)-sfavicon.ico"/>
        <link src="%(STATIC_URL)-ssites/common/c/print.css"/>
        <link src="%(MEDIA_URL)-ssites/common/c/screen.css"/>
        <script src="%(STATIC_URL)-ssites/common/j/jquery.js"/>
        <script>
            var myTestString = "%(STATIC_URL)-sfolder/";
        </script>
        </head>
        <body>
        <img href="%(MEDIA_URL)-sgraphic/first.gif" width="100"
        height="200"/>
        </body>
        </html>
        """ %({
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
              })
        return None

    def tearDown(self):
        """clean up"""
        return None

    def test_static_url_rewrites(self):
        logger.debug(self.response.content)
        replacements = self.cb.calculate_replacements(self.response)
        logger.debug(replacements)
        response = self.cb.process_response(self.request, self.response)
        logger.debug(response.content)
        self.assertEqual(self.response.status_code, 200)
        #assert(False)
        return None

    def test_calc_cachebust(self):
        url_prefix = 'http://s.localhost/'
        fs_path = self.workdir
        path = 'favicon.ico'
        ts = int(os.path.getmtime(os.path.join(self.workdir, path)))
        pair = self.cb.calc_cachebust(url_prefix, fs_path, path)
        self.assertEqual(pair[0], 'http://s.localhost/favicon.ico')
        self.assertEqual(pair[1], 'http://s.localhost/favicon-cb%d.ico' %(ts))

    def test_calculate_replacements(self):
        response = HttpResponse()
        response.content = """
        <script>
        var js="%(STATIC_URL)-s"
        var js="%(STATIC_URL)-sfolder/"
        var js="%(STATIC_URL)-sfolder/file.jpg"
        </script>
        """ %({'STATIC_URL': settings.STATIC_URL, })
        logger.debug(response.content)
        replacements = self.cb.calculate_replacements(response)
        logger.debug(replacements)
