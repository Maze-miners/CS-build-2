from django.db import models

# Create your models here.
class MapRoom(models.Model):
    self.room_id = models.IntegerField()
    self.title = models.CharField(max_length=50)
    self.description = models.CharField(max_length=100)
    self.x = models.IntegerField()
    self.y = models.IntegerField()
    self.neighbors = models.CharField(max_length=250)
