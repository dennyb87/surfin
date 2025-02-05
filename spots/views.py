from django.shortcuts import render

from spots.models import Spot


def spot(request, spot_uid):
    spot = Spot.objects.get(uid=spot_uid)
    return render(
        request=request, template_name="spots/spot.html", context={"spot": spot}
    )
