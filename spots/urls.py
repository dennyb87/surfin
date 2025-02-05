from django.urls import path

from . import views

urlpatterns = [
    path("<str:spot_uid>/", views.spot, name="spots"),
]
