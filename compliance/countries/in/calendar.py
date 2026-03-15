from datetime import date, timedelta
from typing import List, Dict

class IndiaComplianceCalendar:
    """
    Generates compliance deadlines for Indian companies.
    """
    
    def __init__(self, company):
        self.company = company
        self.gstin_type = getattr(company, 'gstin_type', 'regular') # 'regular' or 'qrmp'
        
    def get_deadlines(self, year: int, month: int = None) -> List[Dict]:
        """Get all deadlines for a specific month or full year."""
        
        deadlines = []
        
        # We process from month-1 to month+1 to catch all potential deadlines due in 'month'
        # Or just process the full year if no month is specified
        months_to_process = range(1, 13)
        
        for m in months_to_process:
            # Monthly Tasks
            
            # TDS Payment - 7th of next month (except March, which is April 30th)
            tds_month = m + 1
            tds_year = year
            if tds_month > 12:
                tds_month = 1
                tds_year += 1
            
            if m == 3: # March TDS
                tds_due = date(tds_year, 4, 30)
            else:
                tds_due = date(tds_year, tds_month, 7)
                
            deadlines.append({
                'title': 'TDS Payment / Challan Deposit',
                'description': f'Deposit TDS deducted in {date(year, m, 1).strftime("%B %Y")}',
                'due_date': tds_due,
                'category': 'Tax',
                'priority': 'High'
            })
            
            # GST Requirements based on profile
            if self.gstin_type == 'regular':
                # GSTR-1: 11th of next month
                gstr1_month = m + 1
                gstr1_year = year
                if gstr1_month > 12:
                    gstr1_month = 1
                    gstr1_year += 1
                
                deadlines.append({
                    'title': 'GSTR-1 Return Filing',
                    'description': f'Outward supplies for {date(year, m, 1).strftime("%B %Y")}',
                    'due_date': date(gstr1_year, gstr1_month, 11),
                    'category': 'GST',
                    'priority': 'High'
                })
                
                # GSTR-3B: 20th of next month
                deadlines.append({
                    'title': 'GSTR-3B Return Filing & Tax Payment',
                    'description': f'Summary return for {date(year, m, 1).strftime("%B %Y")}',
                    'due_date': date(gstr1_year, gstr1_month, 20),
                    'category': 'GST',
                    'priority': 'High'
                })
        
        # Quarterly Tasks
        quarters = [
            {'q': 'Q1', 'months': [4, 5, 6], 'due_tds': date(year, 7, 31)},
            {'q': 'Q2', 'months': [7, 8, 9], 'due_tds': date(year, 10, 31)},
            {'q': 'Q3', 'months': [10, 11, 12], 'due_tds': date(year+1, 1, 31)},
            {'q': 'Q4', 'months': [1, 2, 3], 'due_tds': date(year, 5, 31)},
        ]
        
        for quarter in quarters:
            deadlines.append({
                'title': f'TDS Quarterly Return ({quarter["q"]})',
                'description': 'File Form 24Q (Salary) and 26Q (Other)',
                'due_date': quarter['due_tds'],
                'category': 'Tax',
                'priority': 'High'
            })
            
            # QRMP Scheme GST returns
            if self.gstin_type == 'qrmp':
                gstr_due_month = quarter['months'][-1] + 1
                gstr_due_year = year if quarter['months'][-1] != 12 else year + 1
                if gstr_due_month > 12: gstr_due_month = 1
                
                deadlines.append({
                    'title': f'GSTR-1 QRMP Return ({quarter["q"]})',
                    'description': 'IFF or full return',
                    'due_date': date(gstr_due_year, gstr_due_month, 13),
                    'category': 'GST',
                    'priority': 'High'
                })
                
                deadlines.append({
                    'title': f'GSTR-3B QRMP Return ({quarter["q"]})',
                    'description': 'Quarterly summary return',
                    'due_date': date(gstr_due_year, gstr_due_month, 24), # 22nd or 24th based on state
                    'category': 'GST',
                    'priority': 'High'
                })
            
        # Annual Tasks
        deadlines.append({
            'title': 'Income Tax Return (Companies)',
            'description': 'Filing of Income Tax Return for previous FY',
            'due_date': date(year, 10, 31),
            'category': 'Audit',
            'priority': 'High'
        })
        
        deadlines.append({
            'title': 'GSTR-9 Annual Return',
            'description': 'Annual GST Return for previous FY',
            'due_date': date(year, 12, 31),
            'category': 'GST',
            'priority': 'Medium'
        })
        
        deadlines.append({
            'title': 'ROC Filing (AOC-4)',
            'description': 'Financial statements filing with MCA',
            'due_date': date(year, 10, 30), # 30 days from AGM (Assuming Sep 30 AGM)
            'category': 'Corporate',
            'priority': 'Medium'
        })
        
        deadlines.append({
            'title': 'ROC Filing (MGT-7)',
            'description': 'Annual Return filing with MCA',
            'due_date': date(year, 11, 29), # 60 days from AGM
            'category': 'Corporate',
            'priority': 'Medium'
        })
        
        # Sort and return
        deadlines.sort(key=lambda x: x['due_date'])
        
        if month:
            # Filter exactly for requested month
            deadlines = [d for d in deadlines if d['due_date'].month == month and d['due_date'].year == year]
            
        return deadlines
