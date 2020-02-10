from django.contrib import admin

from .models import User, Vehicle, Ride

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    fields = ["username", "email", "password", "isDriver"]
    list_display = ("username", "email", "isDriver")


class VehicleAdmin(admin.ModelAdmin):
    fields = ["v_type", "license_number", "max_number", "comment", "owner"]
    list_display = ("v_type", "license_number", "max_number", "owner")


class RideAdmin(admin.ModelAdmin):
    fields = [
        "owner", "destination", "date", "time", "canShare", "passenger_num",
        "status", "vehicle", "special_info", "driver_id", "sharer"
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Ride, RideAdmin)
