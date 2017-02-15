import urllib.parse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import (authenticate, login, logout,
                                 BACKEND_SESSION_KEY, REDIRECT_FIELD_NAME)
from django.http import HttpResponseRedirect
from django.views.generic.base import View, TemplateView


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


class LoginView(View):
    redirect_field_name = REDIRECT_FIELD_NAME

    def get(self, request):
        username = request.META.get('REMOTE_USER')
        if not username:
            raise ImproperlyConfigured('This view is supposed to set a REMOTE_USER environment variable')

        user = authenticate(username=username)
        login(request, user)

        redirect_to = request.GET.get(self.redirect_field_name, '')
        netloc = urllib.parse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        elif netloc and netloc != request.get_host():
            redirect_to = settings.LOGIN_REDIRECT_URL

        return HttpResponseSeeOther(redirect_to)

class LogoutView(TemplateView):
    template_name = 'webauth/logged_out.html'

    def get(self, request):
        context = {
            'was_webauth': request.session.get(BACKEND_SESSION_KEY) == 'django_webauth.backends.WebauthLDAP',
            'login_redirect_url': settings.LOGIN_REDIRECT_URL,
        }
        logout(request)
        return self.render_to_response(context)

