from django.conf.urls import patterns, url

from .. import views

urlpatterns = patterns('',
    url('^login/$', views.LoginView.as_view(), name='login'),
    url('^logout/$', views.LogoutView.as_view(), name='logout'),
)
