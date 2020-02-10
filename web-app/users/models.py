from django.db import models
from django.utils import timezone
from datetime import datetime
"""
Put blank = True, at whatever field that is not required
"""


class User(models.Model):
    username = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    isDriver = models.BooleanField(default=False)

    def __str__(self):
        return self.username + "  " + self.email


class Vehicle(models.Model):
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="vehicle")
    v_type = models.CharField(max_length=50)
    license_number = models.CharField(max_length=20)
    max_number = models.IntegerField()
    comment = models.TextField(blank=True, default="")

    def __str__(self):
        return self.v_type


class Ride(models.Model):
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="ride_own")
    driver_id = models.IntegerField(default=-1, blank=True)
    canShare = models.BooleanField(default=False)
    sharer = models.ManyToManyField(User,
                                    related_name="ride_share",
                                    blank=True)
    status = models.CharField(
        max_length=20, default="open")  # 1:open, 2:confirmed, 3:complete
    # vehicle type: Car, CarXL, Comfort
    vehicle = models.CharField(max_length=50, default="Car", blank=True)
    destination = models.TextField(max_length=100)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    passenger_num = models.IntegerField()
    special_info = models.TextField(default="", blank=True)

    def shareable(self):
        if self.canShare:
            return "Yes"
        else:
            return "No"        
    
    def get_date_str(self):
        return self.date.strftime("%Y-%m-%d")

    def get_time_str(self):
        return self.time.strftime("%H:%M")

    def get_left_cap(self):
        if self.vehicle == "Comfort":
            total = 8
        elif self.vehicle == "CarXL":
            total = 6
        else:
            total = 4
        return total - self.passenger_num

    def __str__(self):
        return self.destination
