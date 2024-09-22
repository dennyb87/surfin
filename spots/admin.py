from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse

from spots.domain import SpotSnapshotDomain
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
    change_form_template = "admin/assessment_change_form.html"

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context=None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        orm_obj = SnapshotAssessment.objects.get(id=int(object_id)).snapshot
        snapshot = SpotSnapshotDomain.from_orm_obj(orm_obj)
        extra_context["snapshot_data"] = snapshot.to_assessment_format()
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(
        self, request: HttpRequest, form_url: str = "", extra_context=None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        orm_obj = SpotSnapshot.objects.get(id=int(request.GET["snapshot"]))
        snapshot = SpotSnapshotDomain.from_orm_obj(orm_obj)
        extra_context["snapshot_data"] = snapshot.to_assessment_format()
        return super().add_view(request, form_url=form_url, extra_context=extra_context)


admin.site.register(Spot, SpotAdmin)
admin.site.register(SpotSnapshot, SpotSnapshotAdmin)
admin.site.register(SnapshotAssessment, SnapshotAssessmentAdmin)
