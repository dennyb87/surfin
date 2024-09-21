from django.contrib import admin
from django.utils.safestring import mark_safe

from windy.models import WindyWebcamData


# Register your models here.
class WindyWebcamDataAdmin(admin.ModelAdmin):
    readonly_fields = ["thumbnail"]

    def thumbnail(self, obj):
        img_tag = f'<img src="{obj.preview.url}" width="520" height="auto" >'
        return mark_safe(img_tag)


admin.site.register(WindyWebcamData, WindyWebcamDataAdmin)
