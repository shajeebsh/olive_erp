# UAE Tax & Compliance Module (Phase 2E)

The UAE compliance module extends the Olive ERP country framework to support the specific tax and regulatory requirements of the United Arab Emirates.

## Supported Features

### 1. Value Added Tax (VAT)
- **Engine Methods**: Standard rate (5%), Zero rate (0%), and Exempt supplies.
- **VAT 201 Return**: Automatically aggregates sales and purchase data into the FTA-mandated VAT 201 format (Boxes 1-14).
- **Validation**: Strict TRN validation ensuring 15-digit compliance.

### 2. Excise Tax
- **Calculations**: Specific excise rates for categorised goods including:
  - Tobacco products (100%)
  - Energy drinks (100%)
  - Carbonated drinks (50%)
  - Sweetened drinks (50%)
  - Electronic smoking devices (100%)
- **Digital Tax Stamps**: Support for marking excise products that require Digital Tax Stamps (DTS).
- **Declarations**: Generation of monthly excise declarations capturing total excise due.

### 3. Corporate Tax (CT)
- **Standard Rates**: 0% on taxable income up to AED 375,000, and 9% on income exceeding this threshold.
- **Reliefs**: 
  - Small Business Relief implementation.
  - Loss Relief carries forward (capped at 75% of taxable income in any given period).
- **Free Zone Persons**: Special provisions for qualifying Free Zone Persons (0% on qualifying income, standard rates on non-qualifying income exceeding the de minimis threshold of 5% or AED 5,000,000).

### 4. API Integration (FTA)
- Stubs for direct integration with the Federal Tax Authority (FTA) APIs for filing VAT, Excise, and Corporate Tax returns.
- Authenticated JWT token mock setup for seamless backend transmission.

### 5. Compliance Calendar
- Automatically generates filing deadlines and reminders for:
  - VAT returns (Quarterly/Monthly)
  - Excise declarations (Monthly)
  - Corporate Tax returns (Annual - 9 months post financial year)
  - Economic Substance Regulations (ESR) notifications and reports
  - Ultimate Beneficial Owner (UBO) register maintenance

## Installation & Configuration
To use the UAE compliance features, select `AE` (United Arab Emirates) during the company setup wizard. All necessary tax periods, VAT calculations, and regulatory models will automatically load.
