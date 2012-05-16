import sys
from django.conf import settings

def define_setting(name, default, dynamic=True):
    """universal settings definition"""
    this = sys.modules[__name__]
    setattr(this, name, getattr(settings, name, default))

# should we add cachebusters to STATIC_URL links?
define_setting('STATIC_ROOT', 'static/', dynamic=False)
define_setting('STATIC_URL', '/static/', dynamic=False)
define_setting('CACHEBUST_STATIC_URL', 'false')

# should we add cachebusters to MEDIA_URL links? bear in mind that if
# the media url is under the static url, this setting will be "overriden"
# by the CACHEBUST_STATIC_URL setting
define_setting('MEDIA_ROOT', 'media/', dynamic=False)
define_setting('MEDIA_URL', '/media/', dynamic=False)
define_setting('CACHEBUST_MEDIA_URL', 'false')

# should we mangle filenames or simply add cache buster query strings?
define_setting('CACHEBUST_MANGLE_FILENAME', 'false')
