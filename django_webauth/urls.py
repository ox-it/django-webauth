# Try/Except here as Django moved these modules from urls.defaults into urls in
# Django 1.4 leaving proxy objects. These were completely removed in Django 1.6
try:
    from django.conf.urls import patterns, url
except ImportError:
    # Django <1.4
    from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
)
