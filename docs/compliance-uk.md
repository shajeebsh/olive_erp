# UK Compliance Module

This document outlines the implementation details for the United Kingdom tax and compliance module in Olive ERP.

## Features

1. **UK Tax Engine (`compliance/countries/uk/__init__.py`)**
   - VAT calculations (20%, 5%, 0%, exempt)
   - VAT number validation (GB format)
   - 9-box return generation

2. **Making Tax Digital (`compliance/countries/uk/mtd.py`)**
   - HMRC API integration stubs
   - OAuth flow structure

3. **CT600 Corporation Tax (`compliance/countries/uk/ct600.py`)**
   - Corporation tax calculator with marginal relief
   - Trading, property, and interest income computation
   - Capital allowances

4. **Companies House (`compliance/countries/uk/models.py`, `companies_house.py`)**
   - Tracking officers (Directors, Secretaries, LLP Members)
   - PSC (Person with Significant Control) register
   - Confirmation Statement (CS01) filing

5. **PAYE RTI (`compliance/countries/uk/rti.py`)**
   - PAYE / NI calculations
   - Full Payment Submission (FPS) XML generation
   - P60 generation

6. **Compliance Calendar (`compliance/countries/uk/calendar.py`)**
   - Automated deadline tracking for HMRC and Companies House
