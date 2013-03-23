from django.conf import settings

WEBAUTH_LDAP_ENDPOINT = getattr(settings, 'WEBAUTH_LDAP_ENDPOINT',
                                'ldap://ldap.oak.ox.ac.uk:389')

WEBAUTH_CUD_ENDPOINT = getattr(settings, 'WEBAUTH_CUD_ENDPOINT',
                               "https://ws.cud.ox.ac.uk/cudws/rest/search")

WEBAUTH_USER_SOURCE = getattr(settings, 'WEBAUTH_USER_SOURCE',
                              'django_webauth.sources.ldap')
