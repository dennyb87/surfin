from astral import LocationInfo
from astral.sun import sun
from django.core.management.base import BaseCommand
from django.utils import timezone

from spots.domain import SpotDomain


class Command(BaseCommand):
    help = """Fetch latest spots data and crystallise it into a snapshot ready for assessement."""

    class CannotRunOutsideDaylightHours(Exception):
        pass

    def add_arguments(self, parser):
        parser.add_argument("--debug", type=int, default=0)

    def check_sun_time(self):
        now = timezone.now()
        city = LocationInfo(
            name="Rome",
            region="Italy",
            timezone="Europe/Rome",
            latitude=41.8967,
            longitude=12.4822,
        )
        sun_times = sun(city.observer)
        sunrise = sun_times["sunrise"]
        sunset = sun_times["sunset"]
        if sunrise < now < sunset:
            pass
        else:
            raise self.CannotRunOutsideDaylightHours(
                f"\nsunrise: {sunrise.isoformat()}\nnow: {now.isoformat()}\nsunset: {sunset.isoformat()}"
            )

    def handle(self, *args, **options):
        debug = bool(options.get("debug", 0))
        if not debug:
            self.check_sun_time()
        spots = SpotDomain.load_all()
        data = spots.take_snapshots()
        self.stdout.write(self.style.SUCCESS(f"Data collected!\n {data}"))
