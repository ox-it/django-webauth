django-webauth
==============

This core was pulled out of an OUCS project, and has not undergone much testing
beyond its current use. Comments to `infodev@oucs.ox.ac.uk
<mailto:infodev@oucs.ox.ac.uk>`_.

Usage
-----

Django configuration
~~~~~~~~~~~~~~~~~~~~

Add ``'django_webauth'`` to your list of ``INSTALLED_APPS`` in your ``settings.py``.

Add the following to your urlconf::

    url(r'^webauth/', include('django_webauth.urls', 'webauth')),

Add ``'django_webauth.backends.WebauthLDAP'`` to your list of ``AUTHENTICATION_BACKENDS``.

To link to the Webauth views from your templates use ``webauth:login`` and ``webauth:logout`` for url names.

Apache configuration
~~~~~~~~~~~~~~~~~~~~

Install and enable the ``webauth`` module. It's packaged as
``libapache2-webauth`` in Debian, and can be enabled using ``a2enmod webauth``.

Follow the `OUCS documentation
<http://www.oucs.ox.ac.uk/webauth/howto.xml?ID=body.1_div.3>`_, protecting only
the Webauth login view. You may also wish to use the ``WebauthDoLogout``
directive for the logout view.

Proxy configuration
~~~~~~~~~~~~~~~~~~~~

If you wish to run django in a light wsgi container such as uwsgi, gunicorn etc. it is possible to pass the webauth username to the local proxy server by setting an environmental variable in apache as shown below.

The following configuration assumes that the apache mod_proxy is loaded as well as mod_webauth and is placed inside the virtualhost configuration. All directly served URLs such as static must be ignoged by using the syntax shown below::

    <VirtualHost *:443>

    #Add standard site and SSL config here

        ProxyPass / http://localhost:8080/
        ProxyPassReverse / http://localhost:8080/
        ProxyPass /static !
        Alias /static /var/www/chembiohub/chembiohubhome/chembiohub/static


    <Location />
      WebAuthExtraRedirect on
      AuthType WebAuth
      require valid-user
      RequestHeader set "X-WEBAUTH-USER" "%{WEBAUTH_USER}e"
      RequestHeader unset X-Forwarded-Proto

      # set the header for requests using HTTPS
      RequestHeader set X-Forwarded-Proto https env=HTTPS
    </location>

    RequestHeader unset X-Forwarded-Proto

    # set the header for requests using HTTPS
    RequestHeader set X-Forwarded-Proto https env=HTTPS


    <Directory /path/to/my/site/static>
        Options Indexes FollowSymLinks Includes
        AllowOverride All
        Order allow,deny
        Allow from all

    </Directory>
    </VirtualHost>


As the request header has come from Apache it is prepended with HTTP_ by the time it gets to django hence the get statement in views.py.
We must also allow proxying of HTTP requests in the django settings file:

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


LDAP configuration
~~~~~~~~~~~~~~~~~~

Make sure that your Kerberos principle has access to the LDAP directory.

Add something like the following to your crontab to keep your Kerberos ticket alive::

    * * * * * /sbin/start-stop-daemon --start --oknodo --quiet --pidfile /var/run/k5start.pid --exec /usr/bin/k5start -- -b -K 5 -p /var/run/k5start.pid -f /path/to/keytab webauth/aardvark.ox.ac.uk

