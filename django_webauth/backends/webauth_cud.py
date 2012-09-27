import logging
import urllib2
import json

from urllib import urlencode
from urllib2_kerberos import HTTPKerberosAuthHandler
from django.contrib.auth.models import User, Group, UNUSABLE_PASSWORD


logger = logging.getLogger(__name__)


class WebauthCUDBackend(object):
    def __init__(self, cud_endpoint="https://ws.cud.ox.ac.uk/cudws/rest/search"):
        self.cud_endpoint = cud_endpoint

    def authenticate(self, username):
        user, created = User.objects.get_or_create(username=username, defaults={'password': UNUSABLE_PASSWORD})
        if created:
            logger.info("Created user: (%s - id:%s)" % (username, user.id))
        else:
            logger.info("User logged in: (%s - id:%s)" % (username, user.id))
        opener = urllib2.build_opener()
        opener.add_handler(HTTPKerberosAuthHandler())
        query = {'q': 'cud\:cas\:sso_username:%s' % username,
                'format': 'json',
                'history': 'n',
                }
        query = urlencode(query)
        url = "%s?%s" % (self.cud_endpoint, query)
        cud_data = json.load(opener.open(url))
        assert len(cud_data['cudSubjects']) == 1
        subject = cud_data['cudSubjects'][0]
        attributes = {}
        for attr in subject['attributes']:
            attributes[attr['name']] = attr['value']
        user.first_name = attributes['cud:cas:firstname']
        user.last_name = attributes['cud:cas:lastname']
        user.email = attributes['cud:cas:oxford_email']
        for name in attributes['cud:cas:current_affiliation']:
            group, created = Group.objects.get_or_create(name=name)
            user.groups.add(group)
        user.save()
        user.backend = 'django_webauth.backends.webauth_cud.WebauthCUDBackend'
        user.cud_attributes = attributes
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
