from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout, BACKEND_SESSION_KEY, REDIRECT_FIELD_NAME

from django_conneg.views import HTMLView
from django_conneg.http import HttpResponseSeeOther

class LoginView(HTMLView):
    def get(self, request):
        username = request.META.get('REMOTE_USER')
        if not username:
            raise ImproperlyConfigured('This view is supposed to set a REMOTE_USER environment variable')

        user = authenticate(username=username)
        login(request, user)

        return HttpResponseSeeOther(request.GET.get(REDIRECT_FIELD_NAME, settings.LOGIN_REDIRECT_URL))

class LogoutView(HTMLView):
    def get(self, request):
        context = {
            'was_webauth': request.session.get(BACKEND_SESSION_KEY) == 'django_webauth.backends.WebauthBackend',
        }
        logout(request)
        return self.render(request, context, 'webauth/logged_out')

