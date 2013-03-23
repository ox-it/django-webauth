from django.contrib.auth.models import User

from .models import WebauthUser

class WebauthBackend(object):
    # Create a User object if not already in the database?
    create_unknown_user = True

    # Overridden so that backend matching by parameters works as expected
    # (and so we don't get in the way of other authentication schemes)
    def authenticate(self, webauth_username):
        try:
            webauth_user = WebauthUser.objects.get(webauth_username=webauth_username)
        except WebauthUser.DoesNotExist:
            if self.create_unknown_user:
                username = self.clean_username(webauth_username)
                user = User.objects.create(username=username)
                webauth_user = WebauthUser.objects.create(user=user,
                                                          webauth_username=webauth_username)
                self.configure_user(user, webauth_username)
            else:
                return None
        return webauth_user.user

    def clean_username(self, username):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """
        return username

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        return user
