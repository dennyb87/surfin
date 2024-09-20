from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from spots.models import SnapshotAssessment, Spot, SpotSnapshot


class SpotAdmin(admin.ModelAdmin):
    pass


class SpotSnapshotAdmin(admin.ModelAdmin):
    actions = ["make_assessment"]

    list_display = ["__str__", "has_assessment"]

    @admin.display(boolean=True)
    def has_assessment(self, obj):
        try:
            return obj.snapshotassessment is not None
        except SnapshotAssessment.DoesNotExist:
            return False

    @admin.action(description="Create a snapshot assessment")
    def make_assessment(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Cannot assess more than one snapshot at a time!",
                level=messages.WARNING,
            )
        else:
            snapshot_id = queryset.values_list("id", flat=True).first()
            url = reverse("admin:spots_snapshotassessment_add")
            return HttpResponseRedirect(f"{url}?snapshot={snapshot_id}")


class SnapshotAssessmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Spot, SpotAdmin)
admin.site.register(SpotSnapshot, SpotSnapshotAdmin)
admin.site.register(SnapshotAssessment, SnapshotAssessmentAdmin)
