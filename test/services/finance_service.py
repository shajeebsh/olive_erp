import requests
from typing import Optional, Dict, List
from datetime import date
import time

from .base_service import BaseService

class FinanceService(BaseService):
    ENDPOINTS = {
        'accounts': '/finance/accounts/',
        'account_detail': '/finance/accounts/{pk}/',
        'journal_entries': '/finance/journal/',
        'journal_detail': '/finance/journal/{pk}/',
        'invoices': '/finance/invoices/',
        'invoice_detail': '/finance/invoices/{pk}/',
        'budgets': '/finance/budgets/',
        'budget_detail': '/finance/budgets/{pk}/',
    }
    
    def list_accounts(self, company_id: int = None, account_type: str = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if account_type:
            params['account_type'] = account_type
        return self.get(self.ENDPOINTS['accounts'], params=params)
    
    def get_account(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['account_detail'].format(pk=pk))
    
    def create_account(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['accounts'], json=data)
    
    def list_journal_entries(self, company_id: int = None, status: str = None,
                              start_date: date = None, end_date: date = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if status:
            params['status'] = status
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(self.ENDPOINTS['journal_entries'], params=params)
    
    def get_journal_entry(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['journal_detail'].format(pk=pk))
    
    def create_journal_entry(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['journal_entries'], json=data)
    
    def post_journal_entry(self, pk: int) -> requests.Response:
        return self.patch(self.ENDPOINTS['journal_detail'].format(pk=pk), json={'action': 'post'})
    
    def reverse_journal_entry(self, pk: int) -> requests.Response:
        return self.patch(self.ENDPOINTS['journal_detail'].format(pk=pk), json={'action': 'reverse'})
    
    def list_invoices(self, company_id: int = None, customer_id: int = None,
                       status: str = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if customer_id:
            params['customer'] = customer_id
        if status:
            params['status'] = status
        return self.get(self.ENDPOINTS['invoices'], params=params)
    
    def get_invoice(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['invoice_detail'].format(pk=pk))
    
    def create_invoice(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['invoices'], json=data)
    
    def send_invoice(self, pk: int) -> requests.Response:
        return self.post(f"{self.ENDPOINTS['invoice_detail'].format(pk=pk)}/send/")
    
    def mark_invoice_paid(self, pk: int) -> requests.Response:
        return self.patch(self.ENDPOINTS['invoice_detail'].format(pk=pk), json={'status': 'PAID'})
    
    def get_balance_sheet(self, company_id: int, as_of_date: date = None) -> requests.Response:
        params = {'company': company_id}
        if as_of_date:
            params['as_of_date'] = as_of_date.isoformat()
        return self.get('/finance/reports/balance-sheet/', params=params)
    
    def get_profit_loss(self, company_id: int, start_date: date = None, 
                         end_date: date = None) -> requests.Response:
        params = {'company': company_id}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get('/finance/reports/profit-loss/', params=params)
