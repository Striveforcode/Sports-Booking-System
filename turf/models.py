from django.db import models

# Create your models here.

class Contact(models.Model):
    yourName = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobilenumber = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.yourName

class TurfBooking(models.Model):
    time_slot = models.CharField(max_length=12)
    isBooked = models.BooleanField(default=False)
    days = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.time_slot

class BookSlot(models.Model):
    # Change ArrayField to TextField and use a method to handle lists
    week = models.TextField(default="")

    def get_week_list(self):
        return self.week.split(',') if self.week else []

class Time(models.Model):
    name = models.CharField(max_length=200, default="")
    # Change ArrayField to TextField and use a method to handle lists
    week = models.TextField(default="")

    def get_week_list(self):
        return self.week.split(',') if self.week else []

class TurfBooked(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    amount = models.IntegerField()
    selected_date = models.CharField(max_length=200)
    current_date = models.CharField(max_length=200)
    booking_time = models.CharField(max_length=200, default="")
    # Change ArrayField to TextField and use a method to handle lists
    slots = models.TextField(default="")

    def get_slots_list(self):
        return self.slots.split(',') if self.slots else []
    
    payment_id = models.CharField(max_length=100)
    paid = models.BooleanField(default=False)
