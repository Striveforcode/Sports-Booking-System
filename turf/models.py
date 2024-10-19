from django.db import models

# Create your models here.

class Contact(models.Model):
    yourName = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobilenumber = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.yourName


# Updated bookslot model for SQLite
class bookslot(models.Model):
    week = models.JSONField()  # Replacing ArrayField with JSONField
    
    def __str__(self):
        return str(self.week)


# Updated Time model for SQLite
class Time(models.Model):
    name = models.CharField(max_length=200, default="")
    week = models.JSONField()  # Replacing ArrayField with JSONField
    
    def __str__(self):
        return self.name


# Updated TurfBooked model for SQLite
class TurfBooked(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    amount = models.IntegerField()
    selected_date = models.CharField(max_length=200)
    current_date = models.CharField(max_length=200)
    booking_time = models.CharField(max_length=200, default="")
    slots = models.JSONField()  # Replacing ArrayField with JSONField
    
    def __str__(self):
        return self.name

