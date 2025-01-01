from django.contrib import admin

from cftoscana.models import CFTBuoyStation

# Register your models here.


class CFTBuoyStationAdmin(admin.ModelAdmin):
    filter_horizontal = ("spots",)


admin.site.register(CFTBuoyStation, CFTBuoyStationAdmin)
