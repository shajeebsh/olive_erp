from decimal import Decimal
from .models import StockLevel, StockMovement

def update_stock(product, warehouse, quantity, movement_type, reference, user=None):
    """
    Updates stock level and records movement.
    quantity can be positive (addition) or negative (subtraction).
    """
    stock_level, created = StockLevel.objects.get_or_create(
        product=product,
        warehouse=warehouse,
        defaults={'quantity_on_hand': Decimal('0')}
    )
    
    stock_level.quantity_on_hand += Decimal(str(quantity))
    stock_level.save()
    
    StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        quantity=quantity,
        movement_type=movement_type,
        reference=reference,
        created_by=user
    )
    return stock_level
