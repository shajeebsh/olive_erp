import requests
from typing import Optional, Dict, List
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
