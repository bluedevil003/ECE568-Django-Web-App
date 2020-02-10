from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("<int:user_id>/", views.user_detail, name="detail"),
    path("<int:user_id>/edit_info", views.edit_info, name="edit_info"),
    path("<int:user_id>/driver_signup",
         views.driver_signup,
         name="signup_driver"),
    path("<int:user_id>/driver_signout",
         views.driver_signout,
         name="signout_driver"),
    path("<int:user_id>/ride_detail/<int:ride_id>/",
         views.ride_detail,
         name="ride_detail"),
    path("<int:user_id>/ride_detail/<int:ride_id>/confirm_ride",
         views.confirm_ride,
         name="confirm_ride"),
    path("<int:user_id>/ride_detail/<int:ride_id>/complete_ride",
         views.complete_ride,
         name="complete_ride"),
    path("<int:user_id>/ride_confirm/<int:ride_id>",
         views.ride_confirm,
         name="ride_confirm")
]
