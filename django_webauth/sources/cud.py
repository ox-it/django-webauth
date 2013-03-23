from django.contrib.auth.models import Group

import requests
from requests_kerberos import HTTPKerberosAuth

from ..conf import WEBAUTH_CUD_ENDPOINT

def provision_user_details(user, webauth_username):
    query = {'q': 'cud\:cas\:sso_username:%s' % webauth_username,
            'format': 'json',
            'history': 'n',
            }
    cud_data = requests.get(WEBAUTH_CUD_ENDPOINT, params=query, auth=HTTPKerberosAuth()).json
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
