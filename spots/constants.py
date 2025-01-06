from decimal import Decimal

from django.templatetags.static import static


class WaveSizeScore:
    MIN_SCORE = Decimal("0.0")
    MAX_SCORE = Decimal("8.0")
    reference_image = static("wave_size_reference.jpg")
    help_text = """
        Try to assess wave size where:
            FLAT = 0
            KNEES = 1
            HIP = 2
            CHEST = 3
            HEAD = 4
            OVERHEAD = 5
            HEAD_AND_HALF = 6
            DOUBLE_SHOULDER = 7
            DOUBLE_OVERHEAD = 8
    """
