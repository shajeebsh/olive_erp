# Ireland Compliance Module

This document outlines the implementation details for the Ireland tax and compliance module in Olive ERP, covering Revenue Irish Tax and Customs requirements.

## Features

1. **Ireland Tax Engine (`compliance/countries/ie/__init__.py`)**
   - VAT calculations (23%, 13.5%, 4.8%, 0%, exempt).
   - VAT number validation (IE format with check digits).
   - VAT3 return generation for Revenue.
   - Support for bi-monthly, monthly, quarterly, and annual VAT periods.

2. **PAYE / PRSI / USC (`compliance/countries/ie/paye.py`)**
   - Payroll calculations including PAYE (Income Tax), PRSI (Social Insurance), and USC (Universal Social Charge).
   - Emergency tax and Week 1 basis support.
   - P60 and P45 logic stubs.

3. **CT1 Corporation Tax (`compliance/countries/ie/ct1.py`)**
   - Corporation tax computation for Trading Income (12.5%) and Passive Income (25%).
   - Close company surcharge tracking.
   - Capital allowances for plant and machinery.

4. **Register of Beneficial Owners (`compliance/countries/ie/rbo.py`)**
   - Tracking control and ownership for RBO filing.
   - Validating PPSNs for Ireland-resident directors and beneficial owners.

5. **Revenue Online Service (ROS) (`compliance/countries/ie/ros.py`)**
   - Integration stubs for digital certificate authentication with ROS.
   - XML payload generation for VAT and PAYE filings.

6. **Compliance Calendar (`compliance/countries/ie/calendar.py`)**
   - Automated deadline tracking for VAT3, CT1, RBO, and PAYE.
   - Integration with Olive ERP finance module for tax liability reminders.

7. **PDF Generators (`compliance/countries/ie/pdf_generators.py`)**
   - Automated generation of official-style Revenue forms for internal review.
