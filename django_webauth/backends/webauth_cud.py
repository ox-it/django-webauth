import logging
import requests

from django.conf import settings
from django.contrib.auth.models import User, Group, UNUSABLE_PASSWORD
from requests_kerberos import HTTPKerberosAuth


logger = logging.getLogger(__name__)


class WebauthCUDBackend(object):
    def __init__(self):
        self.cud_endpoint = getattr(settings, 'WEBAUTH_CUD_ENDPOINT',
                                    "https://ws.cud.ox.ac.uk/cudws/rest/search")

    def authenticate(self, username):
        user, created = User.objects.get_or_create(username=username,
                                                   defaults={'password': UNUSABLE_PASSWORD})
        if created:
            logger.info("Created user: (%s - id:%s)" % (username, user.id))
        else:
            logger.info("User logged in: (%s - id:%s)" % (username, user.id))
        query = {'q': 'cud\:cas\:sso_username:%s' % username,
                 'format': 'json',
                 'history': 'n',
                 }
        cud_data = requests.get(self.cud_endpoint, params=query, auth=HTTPKerberosAuth()).json
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
