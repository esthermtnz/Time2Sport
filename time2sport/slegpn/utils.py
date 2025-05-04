from decimal import Decimal, ROUND_HALF_UP

BONUS_TYPE_MAP = {
    "annual": "Bono Anual",
    "semester": "Bono Semestral",
    "single": "Bono Sesión Única",
}


def get_bonus_name(bonus_type):
    """Gets the bonus name"""
    return BONUS_TYPE_MAP.get(bonus_type, "Bono Desconocido")


def get_discount(price, is_uam):
    """Verifies if the user has a discount depending on the user type"""
    if is_uam:
        return (price * Decimal('0.1')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        return Decimal('0.00')


def get_total(precio, es_uam):
    """Gets the total price"""
    return precio - get_discount(precio, es_uam)
