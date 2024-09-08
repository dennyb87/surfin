from django.core.management.base import BaseCommand

from demo.models import Spots


class Command(BaseCommand):
    help = "Collect latest available data for any existing source."

    def handle(self, *args, **options):
        for data_source in Spots.get_data_sources():
            data = data_source.collect()
            self.stdout.write(
                self.style.SUCCESS(f"Data collected for source {data_source}: {data}")
            )
