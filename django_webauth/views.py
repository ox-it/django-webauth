import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import (authenticate, login, logout,
                                 BACKEND_SESSION_KEY, REDIRECT_FIELD_NAME)
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


class LoginView(View):
    redirect_field_name = REDIRECT_FIELD_NAME

    def get(self, request):
        username = request.META.get('REMOTE_USER')
        if not username:
            #get the username if mod_proxy is running in front of django as configured in README.rst
            username = request.META.get('HTTP_X_WEBAUTH_USER')
            if not username:   
                raise ImproperlyConfigured('This view is supposed to set a REMOTE_USER environment variable')

        user = authenticate(username=username)
        login(request, user)

        redirect_to = request.GET.get(self.redirect_field_name, '')
        netloc = urlparse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        elif netloc and netloc != request.get_host():
            redirect_to = settings.LOGIN_REDIRECT_URL

        return HttpResponseSeeOther(redirect_to)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return render(request, 'webauth/logged_out', {
            'was_webauth': request.session.get(BACKEND_SESSION_KEY) == 'django_webauth.backends.WebAuthLDAP',
            'login_redirect_url': settings.LOGIN_REDIRECT_URL,
        })
