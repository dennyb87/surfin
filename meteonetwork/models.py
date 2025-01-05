from django.db import models


class MeteoNetworkIRTData(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    snapshot = models.ForeignKey("spots.SpotSnapshot", on_delete=models.CASCADE)
    lat = models.CharField(max_length=1000)
    lon = models.CharField(max_length=1000)
    temperature = models.DecimalField(max_digits=10, decimal_places=4)
    rh = models.DecimalField(max_digits=10, decimal_places=4)
    dew_point = models.DecimalField(max_digits=10, decimal_places=4)
    daily_rain = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    smlp = models.DecimalField(max_digits=10, decimal_places=4)
    wind_direction = models.DecimalField(max_digits=10, decimal_places=4)
    wind_direction_cardinal = models.CharField(max_length=1000)
    wind_speed = models.DecimalField(max_digits=10, decimal_places=4)
    distance = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.__class__.__name__} at {self.created} #{self.pk}"
