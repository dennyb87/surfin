from django.urls import path

from . import views

urlpatterns = [
    path("<str:spot_id>/", views.spot, name="spots"),
]
