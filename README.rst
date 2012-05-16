django_cachebust
================

A simple Django app to handle cache busting for locally served static assets. This app makes
it possible to deliver non-expiring assets for performance in compliance with best practices
such as https://developers.google.com/speed/docs/best-practices/caching

To use this, an apache configuration like this should work::

    <VirtualHost *:80>
        ServerName static.mydomain.com
        ServerAlias static

        ExpiresActive On
        ExpiresDefault "access plus 1 year"
        RewriteEngine On
        RewriteRule (.*)-cb\d+\.(.*)$ $1.$2 [L]

        DocumentRoot /var/www/html
    </VirtualHost>

Other Resources:
  * http://blog.bripkens.de/2012/03/nginx-cache-busting/
