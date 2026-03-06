from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GoodsReceivedNote, PurchaseOrderLine
from inventory.services import update_stock

@receiver(post_save, sender=GoodsReceivedNote)
def update_stock_on_grn(sender, instance, created, **kwargs):
    if created:
        po = instance.purchase_order
        for line in po.lines.all():
            # Assume first warehouse for simplicity, or add warehouse to GRN
            from inventory.models import Warehouse
            warehouse = Warehouse.objects.first() 
            if warehouse:
                update_stock(
                    product=line.product,
                    warehouse=warehouse,
                    quantity=line.quantity,
                    movement_type='PURCHASE',
                    reference=f"GRN: {instance.grn_number}",
                    user=instance.received_by
                )
                line.quantity_received += line.quantity
                line.save()
        
        po.status = 'RECEIVED'
        po.save()
