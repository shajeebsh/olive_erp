import pandas as pd
from django.db import connection
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class ReportEngine:
    """
    Enhanced Reporting Engine for Phase 1 (Feature 13).
    Supports dynamic generation of Balance Sheet, P&L, etc.
    """
    def __init__(self, company):
        self.company = company

    def get_data_from_query(self, query, params=None):
        return pd.read_sql_query(query, connection, params=params)

    def generate_excel(self, data, sheet_name="Report"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=sheet_name)
        return output.getvalue()

    def generate_pdf(self, title, data_summary):
        output = BytesIO()
        p = canvas.Canvas(output, pagesize=letter)
        p.drawString(100, 750, f"Report: {title}")
        p.drawString(100, 730, f"Company: {self.company.company_name}")
        
        y = 700
        for key, value in data_summary.items():
            p.drawString(100, y, f"{key}: {value}")
            y -= 20
            
        p.showPage()
        p.save()
        return output.getvalue()

    def get_balance_sheet(self, date):
        # Placeholder logic for dynamic financial statements
        query = """
            SELECT a.account_type, SUM(l.debit - l.credit) as balance
            FROM finance_account a
            JOIN finance_journalentryline l ON a.id = l.account_id
            JOIN finance_journalentry e ON l.journal_entry_id = e.id
            WHERE a.company_id = %s AND e.date <= %s
            GROUP BY a.account_type
        """
        return self.get_data_from_query(query, [self.company.id, date])

    def get_profit_loss(self, start_date, end_date):
        query = """
            SELECT a.account_type, SUM(l.credit - l.debit) as balance
            FROM finance_account a
            JOIN finance_journalentryline l ON a.id = l.account_id
            JOIN finance_journalentry e ON l.journal_entry_id = e.id
            WHERE a.company_id = %s AND e.date BETWEEN %s AND %s
            AND a.account_type IN ('Income', 'Expense')
            GROUP BY a.account_type
        """
        return self.get_data_from_query(query, [self.company.id, start_date, end_date])
