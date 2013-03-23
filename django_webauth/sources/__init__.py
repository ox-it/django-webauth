from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils.importlib import import_module

from ..conf import WEBAUTH_USER_SOURCE
from ..models import WebauthUser

if WEBAUTH_USER_SOURCE:
    mod = import_module(WEBAUTH_USER_SOURCE)
    provision_user_details = getattr(mod, 'provision_user_details')

    @receiver(user_logged_in)
    def user_logged_in_handler(sender, request, user, **kwargs):
        try:
            webauth_user = user.webauth_user_set.get()
        except WebauthUser.DoesNotExist:
            pass
        else:
            webauth_username = webauth_user.webauth_username
            provision_user_details(user, webauth_username)
