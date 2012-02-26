from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django_conneg.views import HTMLView
from django_conneg.http import HttpResponseSeeOther

class LoginView(HTMLView):
    def get(self, request):
        username = request.META.get('REMOTE_USER')
        if not username:
            raise ImproperlyConfigured('This view is supposed to set a REMOTE_USER environment variable')

        user = authenticate(username=username)
        login(request, user)

        return HttpResponseSeeOther(request.GET.get('next', settings.LOGIN_REDIRECT_VIEW))

class LogoutView(HTMLView):
    def get(self, request):
        logout(request)
        return self.render(request, context, 'webauth/logged_out')

