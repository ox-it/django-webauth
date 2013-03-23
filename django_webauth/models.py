from django.contrib.auth.models import User
from django.db import models

class WebauthUser(models.Model):
    user = models.ForeignKey(User)
    webauth_username = models.CharField(max_length=16)

