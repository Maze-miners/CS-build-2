from django.db import models

# Create your models here.
class MapRoom(models.Model):
    room_id = models.IntegerField()
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    coordinates = models.CharField(max_length=100)
    neighbors = models.CharField(max_length=250)
