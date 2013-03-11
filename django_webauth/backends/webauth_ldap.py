import ldap
import ldap.sasl
import logging
import re

from django.conf import settings
from django.contrib.auth.models import User, Group, UNUSABLE_PASSWORD

logger = logging.getLogger(__name__)


class WebauthLDAPBackend(object):
    def __init__(self):
        self.ldap_endpoint = getattr(settings, 'WEBAUTH_LDAP_ENDPOINT',
                'ldap://ldap.oak.ox.ac.uk:389')

    def authenticate(self, username):
        user, _ = User.objects.get_or_create(username=username, defaults={'password': UNUSABLE_PASSWORD})
        auth = ldap.sasl.gssapi('')
        oakldap = ldap.initialize(self.ldap_endpoint)
        oakldap.start_tls_s()
        oakldap.sasl_interactive_bind_s('', auth)

        results = oakldap.search_s('ou=people,dc=oak,dc=ox,dc=ac,dc=uk',
                                   ldap.SCOPE_SUBTREE,
                                   '(oakPrincipal=krbPrincipalName=%s@OX.AC.UK,cn=OX.AC.UK,cn=KerberosRealms,dc=oak,dc=ox,dc=ac,dc=uk)' % username)

        if not results:
            return None
        person = results[0][1]

        for name, key in (('first_name', 'givenName'),
                          ('last_name', 'sn'),
                          ('email', 'mail')):
            try:
                setattr(user, name, person[key][0])
            except KeyError, e:
                setattr(user, name, '')
                logger.warning("User %s doesn't have a %s", username, key)

        user.groups = self.get_groups(user, person)

        user.save()
        return user

    def get_groups(self, user, person):
        groups = set('status:%s' % s for s in person['oakStatus'])
        for g in person.get('oakITSSFor', ()):
            match = re.match(r'oakGN=ITSS,oakUnitCode=(\w+),ou=units,dc=oak,dc=ox,dc=ac,dc=uk', g)
            if match:
                groups.add('itss:%s' % match.group(1))
            elif g == 'oakGN=ITSS,ou=oucscentral,dc=oak,dc=ox,dc=ac,dc=uk':
                groups.add('itss')
        for u in person.get('eduPersonOrgUnitDN', ()):
            match = re.match(r'oakUnitCode=(\w+),ou=units,dc=oak,dc=ox,dc=ac,dc=uk', u)
            if match:
                groups.add('affiliation:%s' % match.group(1))

        # As per http://www.oucs.ox.ac.uk/services/oak/sp/ldap/index.xml?ID=recommendations
        # if someone has an eduPersonAffiliation of 'member', they are a member
        # of the University
        if 'member' in person.get('eduPersonAffiliation'):
            groups.add('member')

        return set(Group.objects.get_or_create(name=name)[0] for name in groups)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

