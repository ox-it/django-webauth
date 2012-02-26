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

Add ``'django_webauth.backends.WebathBackend'`` to your list of ``AUTHENTICATION_BACKENDS``.

To link to the Webauth views from your templates use ``webauth:login`` and ``webauth:logout`` for url names.

Apache configuration
~~~~~~~~~~~~~~~~~~~~

Install and enable the ``webauth`` module. It's packaged as
``libapache2-webauth`` in Debian, and can be enabled using ``a2enmod webauth``.

Follow the `OUCS documentation
<http://www.oucs.ox.ac.uk/webauth/howto.xml?ID=body.1_div.3>`_, protecting only
the Webauth login view. You may also wish to use the ``WebauthDoLogout``
directive for the logout view.

LDAP configuration
~~~~~~~~~~~~~~~~~~

Make sure that your Kerberos principle has access to the LDAP directory.

Add something like the following to your crontab to keep your Kerberos ticket alive::

    * * * * * /sbin/start-stop-daemon --start --oknodo --quiet --pidfile /var/run/k5start.pid --exec /usr/bin/k5start -- -b -K 5 -p /var/run/k5start.pid -f /path/to/keytab webauth/aardvark.ox.ac.uk

