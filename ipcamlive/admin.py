from django.contrib import admin
from django.utils.safestring import mark_safe

from ipcamlive.models import IPCamLiveData, IPCamLiveWebcam


class IPCamLiveWebcamAdmin(admin.ModelAdmin):
    pass


class IPCamLiveDataAdmin(admin.ModelAdmin):
    readonly_fields = ["thumbnail"]

    def thumbnail(self, obj):
        img_tag = f'<img src="{obj.preview.url}" width="520" height="auto" >'
        return mark_safe(img_tag)


admin.site.register(IPCamLiveWebcam, IPCamLiveWebcamAdmin)
admin.site.register(IPCamLiveData, IPCamLiveDataAdmin)
