import requests
from typing import Optional, Dict, List
from datetime import date
import time

class BaseService:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def set_auth_token(self, token: str):
        self.session.headers.update({'Authorization': f'Token {token}'})
    
    def clear_auth(self):
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def get(self, endpoint: str, params: Dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        response = self.session.get(url, params=params)
        response.elapsed = time.time() - start
        return response
    
    def post(self, endpoint: str, data: Dict = None, json: Dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        response = self.session.post(url, data=data, json=json)
        response.elapsed = time.time() - start
        return response
    
    def put(self, endpoint: str, data: Dict = None, json: Dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        response = self.session.put(url, data=data, json=json)
        response.elapsed = time.time() - start
        return response
    
    def patch(self, endpoint: str, data: Dict = None, json: Dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        response = self.session.patch(url, data=data, json=json)
        response.elapsed = time.time() - start
        return response
    
    def delete(self, endpoint: str) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        response = self.session.delete(url)
        response.elapsed = time.time() - start
        return response
    
    def is_success(self, response: requests.Response) -> bool:
        return response.status_code in range(200, 300)
    
    def is_client_error(self, response: requests.Response) -> bool:
        return response.status_code in range(400, 500)
    
    def is_server_error(self, response: requests.Response) -> bool:
        return response.status_code in range(500, 600)


class HRService(BaseService):
    ENDPOINTS = {
        'employees': '/hr/employees/',
        'employee_detail': '/hr/employees/{pk}/',
        'departments': '/hr/departments/',
        'department_detail': '/hr/departments/{pk}/',
        'leave_requests': '/hr/leave/',
        'leave_detail': '/hr/leave/{pk}/',
        'attendance': '/hr/attendance/',
        'attendance_detail': '/hr/attendance/{pk}/',
        'payslips': '/hr/payslips/',
        'payroll_periods': '/hr/payroll-periods/',
    }
    
    def list_employees(self, company_id: int = None, department_id: int = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if department_id:
            params['department'] = department_id
        return self.get(self.ENDPOINTS['employees'], params=params)
    
    def get_employee(self, pk: int) -> requests.Response:
        return self.get(self.ENDPOINTS['employee_detail'].format(pk=pk))
    
    def create_employee(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['employees'], json=data)
    
    def update_employee(self, pk: int, data: Dict) -> requests.Response:
        return self.patch(self.ENDPOINTS['employee_detail'].format(pk=pk), json=data)
    
    def delete_employee(self, pk: int) -> requests.Response:
        return self.delete(self.ENDPOINTS['employee_detail'].format(pk=pk))
    
    def list_departments(self, company_id: int = None) -> requests.Response:
        params = {'company': company_id} if company_id else {}
        return self.get(self.ENDPOINTS['departments'], params=params)
    
    def create_department(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['departments'], json=data)
    
    def list_leave_requests(self, company_id: int = None, employee_id: int = None, 
                            status: str = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if employee_id:
            params['employee'] = employee_id
        if status:
            params['status'] = status
        return self.get(self.ENDPOINTS['leave_requests'], params=params)
    
    def create_leave_request(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['leave_requests'], json=data)
    
    def approve_leave_request(self, pk: int) -> requests.Response:
        return self.patch(self.ENDPOINTS['leave_detail'].format(pk=pk), json={'status': 'APPROVED'})
    
    def reject_leave_request(self, pk: int) -> requests.Response:
        return self.patch(self.ENDPOINTS['leave_detail'].format(pk=pk), json={'status': 'REJECTED'})
    
    def list_attendance(self, company_id: int = None, employee_id: int = None,
                        start_date: date = None, end_date: date = None) -> requests.Response:
        params = {}
        if company_id:
            params['company'] = company_id
        if employee_id:
            params['employee'] = employee_id
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(self.ENDPOINTS['attendance'], params=params)
    
    def record_attendance(self, data: Dict) -> requests.Response:
        return self.post(self.ENDPOINTS['attendance'], json=data)
