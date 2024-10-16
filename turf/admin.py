from django.contrib import admin
from .models import Contact, TurfBooking, TurfBooked, BookSlot, Time  # Import the Time model as well

# Register your models here.
admin.site.register(Contact)
admin.site.register(TurfBooking)  # Updated from turfBooking to TurfBooking
admin.site.register(TurfBooked)
admin.site.register(BookSlot)      # Make sure this matches the model name (BookSlot)
admin.site.register(Time)          # Don't forget to register the Time model
