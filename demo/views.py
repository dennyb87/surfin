from django.shortcuts import render

from spots.models import Spot


def index(request):
    spots = Spot.objects.all()
    return render(request, "demo/index.html", context={"spots": spots})
