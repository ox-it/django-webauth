import ldap3
import logging
import re

from django.conf import settings
from django.contrib.auth.models import User, Group


logger = logging.getLogger(__name__)


class WebauthLDAP(object):
    # regex to match all groups that this backend manages. Other groups will
    # be left alone, but group memberships matching this pattern will be
    # wipied out if the user is no longer supposed to be a member.
    managed_groups_re = re.compile(r'^(itss$|member$|itss:|affiliation:|status:)')
    person_filter_pattern = \
        '(oakPrincipal=krbPrincipalName={}@OX.AC.UK,cn=OX.AC.UK,cn=KerberosRealms,dc=oak,dc=ox,dc=ac,dc=uk)'

    def __init__(self):
        self.url = getattr(settings, 'WEBAUTH_LDAP_ENDPOINT',
                'ldap://ldap.oak.ox.ac.uk:389')

    def get_ldap_connection(self):
        return ldap3.Connection(self.url,
                                auto_bind=ldap3.AUTO_BIND_TLS_BEFORE_BIND,
                                authentication=ldap3.SASL,
                                sasl_mechanism='GSSAPI',
                                sasl_credentials=(True,))

    def authenticate(self, username):
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()

        ldap_client = self.get_ldap_connection()
        results = ldap_client.search('ou=people,dc=oak,dc=ox,dc=ac,dc=uk',
                                     self.person_filter_pattern.format(username),
                                     search_scope=ldap3.SUBTREE)

        if not results:
            return None
        person = results[0][1]

        for name, key in (('first_name', 'givenName'),
                          ('last_name', 'sn'),
                          ('email', 'mail')):
            try:
                setattr(user, name, person[key][0])
            except KeyError as e:
                setattr(user, name, '')
                logger.warning("User %s doesn't have a %s", username, key)

        user.groups = self.get_groups(user, person)

        user.save()
        return user

    def get_groups(self, user, person):
        # Start with existing non-managed groups
        groups = set(g.name for g in user.groups.all() if not self.managed_groups_re.match(g.name))
        groups |= set('status:%s' % s for s in person['oakStatus'])
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
