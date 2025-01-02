from django.contrib import admin
from django.utils.safestring import mark_safe

from windy.models import WindyWebcam, WindyWebcamData


class WindyWebcamAdmin(admin.ModelAdmin):
    pass


class WindyWebcamDataAdmin(admin.ModelAdmin):
    readonly_fields = ["thumbnail"]

    def thumbnail(self, obj):
        img_tag = f'<img src="{obj.preview.url}" width="520" height="auto" >'
        return mark_safe(img_tag)


admin.site.register(WindyWebcam, WindyWebcamAdmin)
admin.site.register(WindyWebcamData, WindyWebcamDataAdmin)
