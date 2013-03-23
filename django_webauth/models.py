from django.contrib.auth.models import User
from django.db import models

class WebauthUser(models.Model):
    user = models.OneToOneField(User, related_name='webauth')
    username = models.CharField(max_length=16)
