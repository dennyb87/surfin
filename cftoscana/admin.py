from django.contrib import admin

from cftoscana.models import CFTBuoyData, CFTBuoyStation

# Register your models here.


class CFTBuoyStationAdmin(admin.ModelAdmin):
    filter_horizontal = ("spots",)


class CFTBuoyDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(CFTBuoyStation, CFTBuoyStationAdmin)
admin.site.register(CFTBuoyData, CFTBuoyDataAdmin)
