import unittest

from django.contrib.auth.models import Group, User
from django.test import TestCase, RequestFactory
import mock

from .backends import WebauthLDAP
from .views import LoginView, LogoutView

ldap_result = [[None, {
    'givenName': ['Albert'],
    'sn': ['Einstein'],
    'mail': ['albert@example.org'],
    'oakStatus': ['staff'],
    'eduPersonAffiliation': ['member'],
    'eduPersonOrgUnitDN': [
        'oakUnitCode=physics,ou=units,dc=oak,dc=ox,dc=ac,dc=uk'
    ]
}]]

get_ldap_client = mock.MagicMock()
# WebauthLDAP.get_ldap_client().search_s(...)
get_ldap_client.return_value.search_s.return_value = ldap_result


@mock.patch('django_webauth.backends.WebauthLDAP.get_ldap_client',
            get_ldap_client)
class DjangoWebauthTestCase(TestCase):
    username = 'albert'
    
    def setUp(self):
        self.backend = WebauthLDAP()
        self.login_view = LoginView.as_view()
        self.logout_view = LogoutView.as_view()
        self.factory = RequestFactory()

    def tearDown(self):
        Group.objects.all().delete()
        User.objects.all().delete()

    def testAuthenticate(self):
        user = self.backend.authenticate(self.username)
        self.assertTrue(user.is_authenticated())

    @unittest.expectedFailure
    def testExistingGroupsPreserved(self):
        user = User.objects.create_user(self.username)
        group = Group.objects.create(name='scientists')
        user.groups.add(group)

        self.assertIn(group, user.groups.all())
        user = self.backend.authenticate(self.username)
        self.assertIn(group, user.groups.all())

    def testLogoutView(self):
        # assert to make sure we're logged in
        self.assertTrue(self.client.login(username=self.username))
        response = self.client.get('/logout/')
        self.assertTrue(response.context['was_webauth'])
        
        # Log out again, and we won't have been using Webauth the second time.
        response = self.client.get('/logout/')
        self.assertFalse(response.context['was_webauth'])


    def testGroupsCreated(self):
        user = self.backend.authenticate(self.username)
        self.assertEqual(set(g.name for g in user.groups.all()),
                         set(['member',
                              'status:staff',
                              'affiliation:physics']))

if __name__ == '__main__':
    unittest.main()
