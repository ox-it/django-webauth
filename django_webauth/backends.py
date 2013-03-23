from django.contrib.auth.backends import RemoteUserBackend

from .conf import WEBAUTH_PROVISIONED_GROUP

class WebauthBackend(RemoteUserBackend):
    # Overridden so that backend matching by parameters works as expected
    # (and so we don't get in the way of other authentication schemes)
    def authenticate(self, webauth_user):
        return super(WebauthBackend, self).authenticate(remote_user=webauth_user)

    # Adds a group so we know when to sync from a user detail source.
    def configure_user(self, user):
        user.groups.add(WEBAUTH_PROVISIONED_GROUP)
        return user
