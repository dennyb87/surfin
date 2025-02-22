from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from spots.constants import WaveSizeScore
from spots.domain import SpotSnapshotDomain
from spots.models import SnapshotAssessment, SnapshotDiscarded, Spot, SpotSnapshot


class SpotAdmin(admin.ModelAdmin):
    readonly_fields = ("uid",)


class SpotSnapshotAdmin(admin.ModelAdmin):
    actions = ["make_assessment", "discard"]

    list_display = ["__str__", "has_assessment", "create_assessment"]

    @admin.display(boolean=True)
    def has_assessment(self, obj):
        return obj.has_assessment

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(discarded__isnull=True)

    @admin.action(description="Discard snapshots")
    def discard(self, request, queryset):
        discarded_events = []
        for snapshot in queryset:
            discarded = SnapshotDiscarded(snapshot=snapshot)
            discarded_events.append(discarded)
        SnapshotDiscarded.objects.bulk_create(discarded_events)
        self.message_user(
            request,
            f"Succesfully discarded {len(discarded_events)} snapshots!",
            level=messages.SUCCESS,
        )
        return

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

    def create_assessment(self, obj):
        url = reverse("admin:spots_snapshotassessment_add")
        if not obj.has_assessment:
            return mark_safe(f"<a href={url}?snapshot={obj.pk}>create assessment</a>")


class SnapshotAssessmentAdmin(admin.ModelAdmin):
    change_form_template = "admin/assessment_change_form.html"
    readonly_fields = ["wave_size_reference"]

    def wave_size_reference(self, obj):
        img_tag = (
            f'<img src="{WaveSizeScore.reference_image}" width="120" height="auto" >'
        )
        return mark_safe(img_tag)

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
        extra_context["snapshot_data"] = snapshot.to_assessment_view()
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(
        self, request: HttpRequest, form_url: str = "", extra_context=None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        orm_obj = SpotSnapshot.objects.get(id=int(request.GET["snapshot"]))
        snapshot = SpotSnapshotDomain.from_orm_obj(orm_obj)
        extra_context["snapshot_data"] = snapshot.to_assessment_view()
        return super().add_view(request, form_url=form_url, extra_context=extra_context)


class SnapshotDiscardedAdmin(admin.ModelAdmin):
    pass


admin.site.register(Spot, SpotAdmin)
admin.site.register(SpotSnapshot, SpotSnapshotAdmin)
admin.site.register(SnapshotAssessment, SnapshotAssessmentAdmin)
admin.site.register(SnapshotDiscarded, SnapshotDiscardedAdmin)
