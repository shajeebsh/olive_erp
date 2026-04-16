import requests
from typing import Optional, Dict, List
from datetime import date
import time

from .base_service import BaseService

class CRMService(BaseService):
    ENDPOINTS = {
        'customers': '/crm/customers/',
        'customer_detail': '/crm/customers/{pk}/',
        'leads': '/crm/leads/',
        'lead_detail': '/crm/leads/{pk}/',
        'sales_orders': '/crm/sales-orders/',
        'sales_order_detail': '/crm/sales-orders/{pk}/',
        'quotations': '/crm/quotations/',
        'quotation_detail': '/crm/quotations/{pk}/',
    }
    
    def list_customers(self, company_id: int = None, is_active: bool = True) -> requests.Response:
        params = {'is_active': is_active}
        if company_id:
            params['company'] = company_id
        return self.get(self.ENDPOINTS['customers'], params=params)
    
    def get_customer(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['customer_detail'].format(pk=pk))
    
    def create_customer(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['customers'], json=data)
    
    def update_customer(self, pk: int, data: Dict) -> requests.Response:
        return self.patch(self.ENDPOINTS['customer_detail'].format(pk=pk), json=data)
    
    def list_leads(self, company_id: int = None, status: str = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if status:
            params['status'] = status
        return self.get(self.ENDPOINTS['leads'], params=params)
    
    def get_lead(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['lead_detail'].format(pk=pk))
    
    def create_lead(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['leads'], json=data)
    
    def update_lead(self, pk: int, data: Dict) -> requests.Response:
        return self.patch(self.ENDPOINTS['lead_detail'].format(pk=pk), json=data)
    
    def convert_lead_to_customer(self, pk: int) -> requests.Response:
        return self.post(f"{self.ENDPOINTS['lead_detail'].format(pk=pk)}/convert/")
    
    def list_sales_orders(self, company_id: int = None, customer_id: int = None,
                           status: str = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if customer_id:
            params['customer'] = customer_id
        if status:
            params['status'] = status
        return self.get(self.ENDPOINTS['sales_orders'], params=params)
    
    def get_sales_order(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['sales_order_detail'].format(pk=pk))
    
    def create_sales_order(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['sales_orders'], json=data)
    
    def update_sales_order(self, pk: int, data: Dict) -> requests.Response:
        return self.patch(self.ENDPOINTS['sales_order_detail'].format(pk=pk), json=data)
    
    def confirm_sales_order(self, pk: int) -> requests.Response:
        return self.patch(self.ENDPOINTS['sales_order_detail'].format(pk=pk), json={'status': 'CONFIRMED'})
    
    def list_quotations(self, company_id: int = None, customer_id: int = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if customer_id:
            params['customer'] = customer_id
        return self.get(self.ENDPOINTS['quotations'], params=params)
    
    def create_quotation(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['quotations'], json=data)
    
    def convert_quotation_to_order(self, pk: int) -> requests.Response:
        return self.post(f"{self.ENDPOINTS['quotation_detail'].format(pk=pk)}/convert/")
