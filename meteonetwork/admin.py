from django.contrib import admin

from meteonetwork.models import MeteoNetworkIRTData


class MeteoNetworkIRTDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(MeteoNetworkIRTData, MeteoNetworkIRTDataAdmin)
