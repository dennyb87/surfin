from decimal import ROUND_HALF_EVEN, Decimal
from enum import Enum


class WaveSizeScore:
    MIN_SCORE = Decimal("0.0")
    MAX_SCORE = Decimal("3.0")
    help_text = """
        Try to assess surfability where:
            FLAT = 0
            LESSON = 1
            LONGBOARD = 2
            SHORTBOARD = 3
    """

    @classmethod
    def score_to_ratio(cls, score: "Decimal"):
        FOUR_PLACES = Decimal("0.0001")
        return Decimal(score / Decimal(len(cls) - 1)).quantize(
            FOUR_PLACES, rounding=ROUND_HALF_EVEN
        )
