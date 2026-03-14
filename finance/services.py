from .models import BillWiseDetail, PaymentAllocation, JournalEntry
from django.db import transaction

@transaction.atomic
def allocate_payment(journal_entry, bill_id, amount):
    """
    Allocate a payment/receipt journal entry to a specific bill.
    """
    bill = BillWiseDetail.objects.get(id=bill_id)
    
    allocation = PaymentAllocation.objects.create(
        payment_entry=journal_entry,
        bill_detail=bill,
        allocated_amount=amount
    )
    
    # Update the bill's outstanding amount
    bill.update_outstanding()
    return allocation

def get_party_outstanding(company, party_name):
    """
    Get all unpaid bills for a specific party.
    """
    return BillWiseDetail.objects.filter(
        party_name=party_name,
        is_fully_settled=False
    ).order_by('due_date')

def auto_allocate_by_fifo(journal_entry, party_name, total_amount):
    """
    Automatically allocate payment to oldest bills first.
    """
    unpaid_bills = get_party_outstanding(None, party_name) # Adjust company filter if needed
    remaining = total_amount
    
    for bill in unpaid_bills:
        if remaining <= 0:
            break
        
        alloc_amount = min(remaining, bill.outstanding_amount)
        allocate_payment(journal_entry, bill.id, alloc_amount)
        remaining -= alloc_amount
        
    return total_amount - remaining

def get_product_price(product, customer=None, quantity=1):
    """
    Get the best price for a product based on active Price Lists.
    """
    from .models import PriceList, PriceListItem
    from django.utils import timezone
    
    today = timezone.now().date()
    price_lists = PriceList.objects.filter(
        company=product.company,
        is_active=True,
        valid_from__lte=today
    ).filter(
        Q(valid_to__isnull=True) | Q(valid_to__gte=today)
    )
    
    if customer and customer.group:
        price_lists = price_lists.filter(Q(customer_group=customer.group) | Q(customer_group__isnull=True))
    else:
        price_lists = price_lists.filter(customer_group__isnull=True)
        
    price_lists = price_lists.order_with_respect_to('priority') # Simplified logic
    
    for pl in price_lists:
        item = PriceListItem.objects.filter(price_list=pl, product=product, min_quantity__lte=quantity).first()
        if item:
            return item.unit_price
            
    return product.unit_price if hasattr(product, 'unit_price') else 0

def calculate_line_discount(product, customer, quantity, amount):
    """
    Calculate applicable discount based on active Discount Rules.
    """
    from .models import DiscountRule
    from django.utils import timezone
    
    today = timezone.now().date()
    rules = DiscountRule.objects.filter(
        company=product.company,
        is_active=True,
        valid_from__lte=today,
        min_quantity__lte=quantity
    ).filter(
        Q(valid_to__isnull=True) | Q(valid_to__gte=today)
    ).order_by('-priority')
    
    # Filter by customer or group
    if customer:
        rules = rules.filter(Q(customer=customer) | Q(customer_group=customer.group) | Q(customer__isnull=True, customer_group__isnull=True))
    else:
        rules = rules.filter(customer__isnull=True, customer_group__isnull=True)
        
    # Filter by product or category
    rules = rules.filter(Q(product=product) | Q(product_category=product.category) | Q(product__isnull=True, product_category__isnull=True))
    
    best_rule = rules.first()
    if not best_rule:
        return 0
        
    if best_rule.discount_type == 'percentage':
        return amount * (best_rule.value / 100)
    else:
        return best_rule.value
