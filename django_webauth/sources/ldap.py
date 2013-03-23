import logging
import re

from django.contrib.auth.models import Group
import ldap

from ..conf import WEBAUTH_LDAP_ENDPOINT

logger = logging.getLogger(__name__)

def provision_user_details(user):
    auth = ldap.sasl.gssapi('')
    oakldap = ldap.initialize(WEBAUTH_LDAP_ENDPOINT)
    oakldap.start_tls_s()
    oakldap.sasl_interactive_bind_s('', auth)

    results = oakldap.search_s('ou=people,dc=oak,dc=ox,dc=ac,dc=uk',
                               ldap.SCOPE_SUBTREE,
                               '(oakPrincipal=krbPrincipalName=%s@OX.AC.UK,cn=OX.AC.UK,cn=KerberosRealms,dc=oak,dc=ox,dc=ac,dc=uk)' % user.username)

    if not results:
        return None
    person = results[0][1]

    for name, key in (('first_name', 'givenName'),
                      ('last_name', 'sn'),
                      ('email', 'mail')):
        try:
            setattr(user, name, person[key][0])
        except KeyError:
            setattr(user, name, '')
            logger.warning("User %s doesn't have a %s", user.username, key)

    user.groups = _get_groups(user, person)

    user.save()

def _get_groups(self, user, person):
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
