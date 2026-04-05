from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from django.core.files.base import ContentFile
from tax_engine.countries.ie.models import (
    IrelandVATReturn, IrelandCTReturn, IrelandCROReturn,
    IrelandRBOFiling, IrelandPAYEReturn
)
import os


class IrelandPDFGenerator:
    """
    PDF generator for Ireland-specific compliance forms.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles for Irish forms."""
        # Add custom styles for Irish government forms
        self.styles.add(ParagraphStyle(
            name='IrishHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='IrishSubheader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            alignment=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='IrishNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_vat3_form(self, vat_return):
        """
        Generate VAT3 form (Ireland VAT Return).
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        # Header
        story.append(Paragraph("VAT RETURN FORM VAT3", self.styles['IrishHeader']))
        story.append(Paragraph("Commissioners for Revenue", self.styles['IrishSubheader']))
        story.append(Spacer(1, 12))
        
        # Company Information
        company_info = [
            ['VAT Number:', vat_return.vat_number or 'Pending'],
            ['Tax Period:', vat_return.vat_period],
            ['Company Name:', vat_return.filing.company.name],
            ['Address:', vat_return.filing.company.registered_address or '']
        ]
        
        company_table = Table(company_info, colWidths=[2*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(company_table)
        story.append(Spacer(1, 12))
        
        # VAT Calculation
        vat_data = [
            ['Description', 'Amount (€)'],
            ['VAT on Sales', f"{vat_return.vat_on_sales:.2f}"],
            ['VAT on Purchases', f"{vat_return.vat_on_purchases:.2f}"],
            ['Net VAT Payable', f"{vat_return.net_vat_payable:.2f}"],
            ['VAT Reclaimable', f"{vat_return.total_vat_reclaimable:.2f}"]
        ]
        
        vat_table = Table(vat_data, colWidths=[3*inch, 2*inch])
        vat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(vat_table)
        story.append(Spacer(1, 12))
        
        # Declaration
        declaration = Paragraph(
            "I declare that the information given in this return is true and complete.",
            self.styles['IrishNormal']
        )
        story.append(declaration)
        
        doc.build(story)
        
        buffer.seek(0)
        return ContentFile(buffer.getvalue(), name=f"vat3_return_{vat_return.vat_period}.pdf")
    
    def generate_ct1_form(self, ct_return):
        """
        Generate CT1 form (Ireland Corporation Tax Return).
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        # Header
        story.append(Paragraph("CORPORATION TAX RETURN FORM CT1", self.styles['IrishHeader']))
        story.append(Paragraph("Commissioners for Revenue", self.styles['IrishSubheader']))
        story.append(Spacer(1, 12))
        
        # Company Information
        company_info = [
            ['CT Number:', ct_return.ct_number or 'Pending'],
            ['Accounting Period End:', ct_return.accounting_period_end.strftime('%Y-%m-%d')],
            ['Company Name:', ct_return.filing.company.name],
            ['Company Number:', ct_return.filing.company.cro_number or '']
        ]
        
        company_table = Table(company_info, colWidths=[2*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(company_table)
        story.append(Spacer(1, 12))
        
        # Tax Calculation
        tax_data = [
            ['Description', 'Amount (€)'],
            ['Taxable Profit', f"{ct_return.taxable_profit:.2f}"],
            ['Corporation Tax Rate', f"{ct_return.ct_rate}%"],
            ['CT Liability', f"{ct_return.ct_liability:.2f}"],
            ['Preliminary Tax Paid', f"{ct_return.preliminary_tax_paid:.2f}"],
            ['Balance Due', f"{ct_return.balance_due:.2f}"]
        ]
        
        tax_table = Table(tax_data, colWidths=[3*inch, 2*inch])
        tax_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(tax_table)
        story.append(Spacer(1, 12))
        
        # Declaration
        declaration = Paragraph(
            "I declare that the information given in this return is true and complete.",
            self.styles['IrishNormal']
        )
        story.append(declaration)
        
        doc.build(story)
        
        buffer.seek(0)
        return ContentFile(buffer.getvalue(), name=f"ct1_return_{ct_return.accounting_period_end.strftime('%Y%m')}.pdf")
    
    def generate_b1_form(self, cro_return):
        """
        Generate B1 form (Ireland CRO Annual Return).
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        # Header
        story.append(Paragraph("ANNUAL RETURN FORM B1", self.styles['IrishHeader']))
        story.append(Paragraph("Companies Registration Office", self.styles['IrishSubheader']))
        story.append(Spacer(1, 12))
        
        # Company Information
        company_info = [
            ['CRO Number:', cro_return.cro_number or 'Pending'],
            ['Annual Return Date:', cro_return.annual_return_date.strftime('%Y-%m-%d')],
            ['Company Name:', cro_return.filing.company.name],
            ['Company Type:', cro_return.get_company_type_display()],
            ['Registered Office:', cro_return.registered_office]
        ]
        
        company_table = Table(company_info, colWidths=[2*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(company_table)
        story.append(Spacer(1, 12))
        
        # Share Capital
        share_data = [
            ['Authorized Share Capital', f"€{cro_return.authorized_share_capital:.2f}"],
            ['Issued Share Capital', f"€{cro_return.issued_share_capital:.2f}"],
            ['Number of Shares', str(cro_return.number_of_shares)]
        ]
        
        share_table = Table(share_data, colWidths=[3*inch, 2*inch])
        share_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(share_table)
        story.append(Spacer(1, 12))
        
        # Director Information
        director_info = Paragraph(
            f"Number of Directors: {cro_return.number_of_directors}",
            self.styles['IrishNormal']
        )
        story.append(director_info)
        
        # Financial Statements
        financial_info = Paragraph(
            f"Financial Statements Attached: {'Yes' if cro_return.financial_statements_attached else 'No'}",
            self.styles['IrishNormal']
        )
        story.append(financial_info)
        
        doc.build(story)
        
        buffer.seek(0)
        return ContentFile(buffer.getvalue(), name=f"b1_return_{cro_return.annual_return_date.strftime('%Y%m')}.pdf")
    
    def generate_rbo_form(self, rbo_filing):
        """
        Generate RBO filing form.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        # Header
        story.append(Paragraph("BENEFICIAL OWNERSHIP REGISTER FILING", self.styles['IrishHeader']))
        story.append(Paragraph("Register of Beneficial Ownership", self.styles['IrishSubheader']))
        story.append(Spacer(1, 12))
        
        # Filing Information
        filing_info = [
            ['RBO Number:', rbo_filing.rbo_number or 'Pending'],
            ['Filing Type:', rbo_filing.get_filing_type_display()],
            ['Company Name:', rbo_filing.filing.company.name],
            ['CRO Number:', rbo_filing.filing.company.cro_number or '']
        ]
        
        filing_table = Table(filing_info, colWidths=[2*inch, 3*inch])
        filing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(filing_table)
        story.append(Spacer(1, 12))
        
        # Beneficial Owners
        owners_info = Paragraph(
            f"Number of Beneficial Owners: {len(rbo_filing.beneficial_owners)}",
            self.styles['IrishNormal']
        )
        story.append(owners_info)
        
        total_percentage = Paragraph(
            f"Total Percentage Owned: {rbo_filing.total_percentage_owned}%",
            self.styles['IrishNormal']
        )
        story.append(total_percentage)
        
        # Presenter Information
        presenter_info = [
            ['Presenter Name:', rbo_filing.presenter_name],
            ['Presenter Email:', rbo_filing.presenter_email],
            ['Presenter Phone:', rbo_filing.presenter_phone]
        ]
        
        presenter_table = Table(presenter_info, colWidths=[2*inch, 3*inch])
        presenter_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(presenter_table)
        
        doc.build(story)
        
        buffer.seek(0)
        return ContentFile(buffer.getvalue(), name=f"rbo_filing_{rbo_filing.filing_date.strftime('%Y%m%d') if rbo_filing.filing_date else 'draft'}.pdf")
    
    def generate_paye_form(self, paye_return):
        """
        Generate PAYE/PRSI return form.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        
        # Header
        story.append(Paragraph("PAYE/PRSI RETURN", self.styles['IrishHeader']))
        story.append(Paragraph("Revenue Commissioners", self.styles['IrishSubheader']))
        story.append(Spacer(1, 12))
        
        # Return Information
        return_info = [
            ['ROS Number:', paye_return.ros_number or 'Pending'],
            ['Employer Reg Number:', paye_return.employer_reg_number or ''],
            ['Period:', f"{paye_return.period_start.strftime('%Y-%m-%d')} to {paye_return.period_end.strftime('%Y-%m-%d')}"],
            ['Return Period:', paye_return.get_return_period_display()]
        ]
        
        return_table = Table(return_info, colWidths=[2*inch, 3*inch])
        return_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(return_table)
        story.append(Spacer(1, 12))
        
        # Payment Details
        payment_data = [
            ['Description', 'Amount (€)'],
            ['Total PAYE Deducted', f"{paye_return.total_paye_deducted:.2f}"],
            ['Total PRSI Deducted', f"{paye_return.total_prsi_deducted:.2f}"],
            ['Total USC Deducted', f"{paye_return.total_usc_deducted:.2f}"],
            ['Total Payment Due', f"{paye_return.total_payment_due:.2f}"],
            ['Payment Made', 'Yes' if paye_return.payment_made else 'No']
        ]
        
        payment_table = Table(payment_data, colWidths=[3*inch, 2*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(payment_table)
        
        doc.build(story)
        
        buffer.seek(0)
        return ContentFile(buffer.getvalue(), name=f"paye_return_{paye_return.period_end.strftime('%Y%m')}.pdf")