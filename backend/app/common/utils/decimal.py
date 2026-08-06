from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator

# Порог «обнуления»: значения меньше 1e-12 (0.0001 сатоши) — это шум
# float-арифметики из JS (quantity = amount / price), а не реальные остатки.
EPSILON = Decimal('1e-12')


def clean_decimal(value: Decimal | None) -> Decimal | None:
    """Normalize a Decimal, collapsing near-zero values and trailing zeros."""
    if value is None:
        return None
    if not isinstance(value, Decimal):
        return value
    if abs(value) < EPSILON:
        return Decimal(0)
    return value.normalize()


CleanDecimal = Annotated[Decimal, AfterValidator(clean_decimal)]
