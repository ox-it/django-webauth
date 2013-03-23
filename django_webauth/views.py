import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import authenticate, login, logout, BACKEND_SESSION_KEY, REDIRECT_FIELD_NAME

from django_conneg.views import HTMLView
from django_conneg.http import HttpResponseSeeOther

class LoginView(HTMLView):
    redirect_field_name = REDIRECT_FIELD_NAME

    def get(self, request):
        webauth_user = request.META.get('REMOTE_USER')
        if not webauth_user:
            raise ImproperlyConfigured('This view is supposed to set a REMOTE_USER environment variable')

        user = authenticate(webauth_user=webauth_user)
        login(request, user)

        redirect_to = request.GET.get(self.redirect_field_name, '')
        netloc = urlparse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        elif netloc and netloc != request.get_host():
            redirect_to = settings.LOGIN_REDIRECT_URL

        return HttpResponseSeeOther(redirect_to)

class LogoutView(HTMLView):
    def get(self, request):
        context = {
            'was_webauth': request.session.get(BACKEND_SESSION_KEY) == 'django_webauth.backends.WebauthBackend',
            'login_redirect_url': settings.LOGIN_REDIRECT_URL,
        }
        logout(request)
        return self.render(request, context, 'webauth/logged_out')

