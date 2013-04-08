from django.contrib.auth.models import User

from .models import WebauthUser

class WebauthBackend(object):
    # Create a User object if not already in the database?
    create_unknown_user = True

    # If there's no WebauthUser, but a user with the right cleaned username,
    # setting this to True will link the created WebauthUser to the existing
    # user. If False, an error will be raised.
    link_to_existing_users = True

    def authenticate(self, webauth_username):
        try:
            return User.objects.get(webauth__username=webauth_username)
        except WebauthUser.DoesNotExist:
            if self.create_unknown_user:
                username = self.clean_username(webauth_username)
                if self.link_to_existing_users:
                    user, _ = User.objects.get_or_create(username=username)
                else:
                    user = User.objects.create(username=username)
                webauth_user = WebauthUser.objects.create(user=user,
                                                          username=webauth_username)
                self.configure_user(user, webauth_username)
            return user

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
