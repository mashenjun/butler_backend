from django.db import models

# Create your models here.


class Person(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

class ProcessedReceipt(models.Model):
    url = models.URLField()
    processedResult = models.TextField()
    isChanged = models.BooleanField()
