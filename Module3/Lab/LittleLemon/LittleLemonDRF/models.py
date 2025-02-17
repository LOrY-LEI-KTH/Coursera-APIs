from django.db import models
from django.contrib.auth.models import User


class Rating(models.Model):
  menuitem_id = models.SmallIntegerField()
  rating = models.SmallIntegerField()
  user = models.ForeignKey(User, on_delete=models.CASCADE)