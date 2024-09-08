from decimal import ROUND_HALF_EVEN, Decimal

from django.db.models import IntegerChoices


class WaveType(IntegerChoices):
    FLAT = 0
    LESSON = 1
    LONGBOARD = 2
    SHORTBOARD = 3

    @classmethod
    def score_to_ratio(cls, score: "Decimal"):
        FOUR_PLACES = Decimal("0.0001")
        return Decimal(score / Decimal(len(cls) - 1)).quantize(
            FOUR_PLACES, rounding=ROUND_HALF_EVEN
        )
