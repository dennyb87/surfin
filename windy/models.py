from django.db import models


# Create your models here.
class WindyWebcamData(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    spot = models.ForeignKey("spots.Spot", on_delete=models.PROTECT)
    windy_webcam_id = models.IntegerField()
    title = models.CharField(max_length=1000)
    view_count = models.IntegerField()
    status = models.CharField(max_length=1000)
    last_updated_on = models.CharField(max_length=1000)
    preview = models.CharField(max_length=1000)
