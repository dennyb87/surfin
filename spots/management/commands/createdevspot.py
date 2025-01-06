from django.core.management.base import BaseCommand

from spots.fixtures import PontileTonfano


class Command(BaseCommand):
    help = """Create dev spot ready for data collection."""

    def handle(self, *args, **options):
        spot = PontileTonfano.create()
        self.stdout.write(self.style.SUCCESS(f"Spot {spot} created!"))
