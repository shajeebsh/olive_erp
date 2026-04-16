import requests
from typing import Optional, Dict, List
from datetime import date
import time

from .base_service import BaseService

class InventoryService(BaseService):
    ENDPOINTS = {
        'products': '/inventory/products/',
        'product_detail': '/inventory/products/{pk}/',
        'warehouses': '/inventory/warehouses/',
        'warehouse_detail': '/inventory/warehouses/{pk}/',
        'stock_levels': '/inventory/stock-levels/',
        'stock_movements': '/inventory/stock-movements/',
    }
    
    def list_products(self, company_id: int = None, category_id: int = None,
                       is_active: bool = True) -> requests.Response:
        params = {'is_active': is_active}
        if company_id:
            params['company'] = company_id
        if category_id:
            params['category'] = category_id
        return self.get(self.ENDPOINTS['products'], params=params)
    
    def get_product(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['product_detail'].format(pk=pk))
    
    def create_product(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['products'], json=data)
    
    def update_product(self, pk: int, data: Dict) -> requests.Response:
        return self.patch(self.ENDPOINTS['product_detail'].format(pk=pk), json=data)
    
    def delete_product(self, pk: int) -> requests.Response:
        return self.delete(self.ENDPOINTS['product_detail'].format(pk=pk))
    
    def list_warehouses(self, company_id: int = None) -> requests.Response:
        params = {'company': company_id} if company_id else {}
        return self.get(self.ENDPOINTS['warehouses'], params=params)
    
    def create_warehouse(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['warehouses'], json=data)
    
    def get_stock_levels(self, company_id: int = None, product_id: int = None,
                          warehouse_id: int = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if product_id:
            params['product'] = product_id
        if warehouse_id:
            params['warehouse'] = warehouse_id
        return self.get(self.ENDPOINTS['stock_levels'], params=params)
    
    def get_stock_movements(self, company_id: int = None, product_id: int = None,
                             start_date: date = None, end_date: date = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if product_id:
            params['product'] = product_id
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(self.ENDPOINTS['stock_movements'], params=params)
    
    def record_stock_receipt(self, data: Dict) -> requests.Response:
        return self.post(f"{self.ENDPOINTS['stock_movements']}receipt/", json=data)
    
    def record_stock_issue(self, data: Dict) -> requests.Response:
        return self.post(f"{self.ENDPOINTS['stock_movements']}issue/", json=data)
    
    def get_low_stock_alerts(self, company_id: int) -> requests.Response:
        return self.get(self.ENDPOINTS['products'], params={'company': company_id, 'low_stock': True})
