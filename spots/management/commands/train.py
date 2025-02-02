from django.core.management.base import BaseCommand

from spots.analytics.domain import WSS1hPredictor


class Command(BaseCommand):
    help = """Train models"""

    def add_arguments(self, parser):
        parser.add_argument("--store", type=int, default=0)
        parser.add_argument("--spot", type=str, required=True)

    def handle(self, *args, **options):
        store = bool(options.get("store"))
        spot_uid = options.get("spot")

        out = WSS1hPredictor.train(spot_uid=spot_uid, store=store)
        if out.stored:
            self.stdout.write(self.style.SUCCESS(f"{out.filename} stored!"))
        self.stdout.write(self.style.SUCCESS(f"Root Mean Squared Error: {out.rmse}"))
