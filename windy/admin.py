from django.contrib import admin

from windy.models import WindyWebcamData


# Register your models here.
class WindyWebcamDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(WindyWebcamData, WindyWebcamDataAdmin)
