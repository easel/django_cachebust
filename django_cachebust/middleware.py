import os
import re

from . import logger

import settings 

class CacheBustMiddleware(object):
    """
    middleware implementing cache busting modification for all
    static asset calls
    """
    def __init__(self):
        self.static_expressions = (
            re.compile('"' + settings.STATIC_URL + '([^"]*)"', re.IGNORECASE),
        )
        self.static_local_expressions = (
            re.compile('"' + settings.STATIC_LOCAL_URL + '([^"]*)"', re.IGNORECASE),
        )
        self.media_expressions = (
            re.compile('"' + settings.MEDIA_URL + '([^"]*)"', re.IGNORECASE),
        )

    def calculate_replacements(self, response):
        replacements = list()
        try:
            if str(settings.CACHEBUST_STATIC_URL).lower() == 'true':
                static_paths, static_local_paths, media_paths = ([], [], [])
                for exp in self.static_expressions:
                    static_paths.extend(exp.findall(response.content)) 
                replacements.extend([ self.calc_cachebust(settings.STATIC_URL,
                                      settings.STATIC_ROOT, path) 
                                      for path in static_paths ])

            if str(settings.CACHEBUST_MEDIA_URL).lower() == 'true':
                for exp in self.media_expressions:
                    media_paths.extend(exp.findall(response.content))   
                replacements.extend([ self.calc_cachebust(settings.MEDIA_URL,
                                      settings.MEDIA_ROOT, path) 
                                      for path in media_paths ])
        except:
            # naked except to keep missing settings from killing pageviews for
            # ajax calls 
            # TODO: fix settings so they are always available
            pass
        return replacements
    
    def process_response(self, request, response):
        """
        process the html results of a given query, replacing requests for
        files under STATIC_URL and STATIC_LOCAL_URL with the their equivalent
        cache busted url
        
        In order for this to work properly, you'll need to ensure that your
        web server is equipped to serve files disregarding the trailing -cb\d+
        prior to the filename extension. For apache, this might look something
        like this:
                RewriteEngine On
                RewriteRule (.*)-cb\d+\.(.*)$ $1.$2 [L]

        In addition, to get the benefit from this, you'll need to set far
        future expires headers. Using Apache, this might look like this:
                ExpiresActive On
                ExpiresDefault "access plus 1 year"
        """
        replacements = self.calculate_replacements(response)
        for replacement in replacements:
            response.content = response.content.replace(replacement[0], replacement[1])

        return response

    @staticmethod
    def calc_cachebust(url_prefix, fs_path, path):
        """
        cachebust a path, given a provided url_path and fs_path. if 
        the CACHEBUST_MANGLE_FILENAME setting is set it will generate
        "filename" cachebusters which must be explictly accounted for on
        the http server. Otherwise it will generate "compatible" query 
        string cachebusters
        """
        local_path = os.path.join(fs_path, path)
        pre, ext = os.path.splitext(path)

        try:
            if os.path.isfile(local_path):
                mstr = '-cb' + str(int(os.path.getmtime(local_path)))
            else:
                mstr = ''
        except:
            mstr = ''
        if str(settings.CACHEBUST_MANGLE_FILENAME).lower() == 'true':
            return (url_prefix + path, url_prefix + pre + mstr + ext)
        else:
            return (url_prefix + path, url_prefix + pre + ext + '?' + mstr)


UNMANGLE_RE = re.compile("-cb[0-9]{7,30}", re.IGNORECASE)

def unmangle_cachebusted( s_url ):
    '''
    Clean out the cachebust code from a url string
    
    '''
    return UNMANGLE_RE.sub("", s_url)

