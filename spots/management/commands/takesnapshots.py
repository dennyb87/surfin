from django.core.management.base import BaseCommand

from spots.domain import SpotDomain


class Command(BaseCommand):
    help = """Fetch latest spots data and crystallise it into a snapshot ready for assessement."""

    def handle(self, *args, **options):
        spots = SpotDomain.load_all()
        data = spots.take_snapshots()
        self.stdout.write(self.style.SUCCESS(f"Data collected!\n {data}"))
