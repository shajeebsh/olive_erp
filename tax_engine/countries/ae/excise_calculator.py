"""
Excise Tax calculation engine
"""
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional

class ExciseCalculator:
    """
    Calculate Excise Tax on designated goods
    """
    
    def __init__(self, company):
        self.company = company
    
    def calculate_excise_due(self, product_id: int, quantity: Decimal,
                             retail_price: Decimal) -> Dict:
        """
        Calculate excise tax for a product
        """
        from .excise import ExciseProduct
        
        try:
            excise_product = ExciseProduct.objects.get(product_id=product_id)
        except ExciseProduct.DoesNotExist:
            return {'error': 'Product not subject to excise tax'}
        
        rate = excise_product.effective_rate
        
        # Excise is calculated on retail price (excluding VAT)
        excise_amount = (retail_price * rate / Decimal('100')) * quantity
        excise_amount = excise_amount.quantize(Decimal('0.01'))
        
        total_with_excise = retail_price * quantity + excise_amount
        
        return {
            'product': excise_product.product.name,
            'category': excise_product.category.display_name,
            'rate': float(rate),
            'quantity': float(quantity),
            'retail_price_per_unit': float(retail_price),
            'total_retail_value': float(retail_price * quantity),
            'excise_amount': float(excise_amount),
            'total_with_excise': float(total_with_excise.quantize(Decimal('0.01'))),
            'requires_digital_stamp': excise_product.has_digital_stamp,
            'stamp_identifier': excise_product.stamp_identifier or None,
        }
    
    def generate_monthly_declaration(self, year: int, month: int) -> Dict:
        """
        Generate monthly excise declaration
        """
        from finance.models import Invoice
        from .excise import ExciseDeclaration, ExciseDeclarationLine
        from django.db.models import Sum
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get sales invoices with excise products
        excise_invoices = Invoice.objects.filter(
            company=self.company,
            issue_date__range=[start_date, end_date],
            items__product__exciseproduct__isnull=False
        ).distinct()
        
        # Group by product category
        categories = {}
        total_excise = Decimal('0.00')
        
        for invoice in excise_invoices:
            for item in invoice.items.all():
                if hasattr(item.product, 'exciseproduct'):
                    excise_product = item.product.exciseproduct
                    category = excise_product.category
                    
                    if category.id not in categories:
                        categories[category.id] = {
                            'category': category,
                            'quantity': Decimal('0.00'),
                            'total_retail': Decimal('0.00'),
                            'excise': Decimal('0.00'),
                        }
                    
                    retail_price = item.unit_price  # Assuming price excludes VAT
                    excise = (retail_price * excise_product.effective_rate / Decimal('100')) * item.quantity
                    
                    categories[category.id]['quantity'] += item.quantity
                    categories[category.id]['total_retail'] += retail_price * item.quantity
                    categories[category.id]['excise'] += excise
                    total_excise += excise
        
        return {
            'period': {
                'year': year,
                'month': month,
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'due_date': self.get_excise_due_date(year, month).isoformat(),
            },
            'categories': [
                {
                    'name': cat['category'].display_name,
                    'quantity': float(cat['quantity']),
                    'total_retail': float(cat['total_retail']),
                    'excise': float(cat['excise']),
                    'rate': float(cat['category'].rate),
                }
                for cat in categories.values()
            ],
            'total_excise_due': float(total_excise),
        }
    
    def get_excise_due_date(self, year: int, month: int) -> date:
        """Excise due date is 28th of following month"""
        if month == 12:
            return date(year + 1, 1, 28)
        return date(year, month + 1, 28)
