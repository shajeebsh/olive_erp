# India Tax & Compliance Documentation

The India country module for Olive ERP provides a complete solution for GST, TDS, E-Way Bill, and E-Invoicing requirements.

## 1. GST (Goods and Services Tax)

### Tax Calculation
The `IndiaTaxEngine` handles CGST, SGST, IGST, and UTGST based on:
- **State Code**: Determined by the first two digits of the GSTIN (e.g., '27' for Maharashtra).
- **Intra-state**: Applied when the source and destination are in the same state (CGST + SGST).
- **Inter-state**: Applied when the source and destination are in different states (IGST).

### HSN/SAC Codes
- **HSN**: Harmonized System of Nomenclature for goods.
- **SAC**: Service Accounting Code for services.
- Models at `compliance/countries/in/models.py` allow mapping products to these codes with their respective GST rates.

### Returns
- **GSTR-1**: Outward supply details.
- **GSTR-3B**: Monthly summary return with tax payment.
- Data can be generated via the `IndiaTaxEngine.generate_tax_return()` method.

## 2. TDS (Tax Deducted at Source)

### Configuration
- Define TDS Sections (e.g., 194C, 194J) with applicable rates and thresholds.
- **Thresholds**: Supports both single-bill limits and annual aggregate limits.

### Processing
- `TDSCalculator` verifies transaction amounts against vendor's aggregated totals for the financial year.
- Automatically triggers TDS deduction if thresholds are crossed.

## 3. Regulatory Compliance

### E-Way Bill
- Required for movement of goods exceeding ₹50,000.
- `EWayBillGenerator` (in `ewaybill.py`) handles data preparation for the NIC portal.

### E-Invoicing (IRN)
- Mandated for businesses exceeding turnover thresholds.
- Tracks `Invoice Reference Number (IRN)` and `Acknowledgement` details in the `EInvoiceIRN` model.

### Compliance Calendar
- Tracks deadlines for:
    - **GST**: GSTR-1 (11th), GSTR-3B (20th).
    - **TDS**: Monthly payment (7th), Quarterly filing (31st).
    - **ROC**: Annual filings (AOC-4, MGT-7).
    - **Income Tax**: Annual return (Oct 31).

## 4. Integration Details

### Extended Models
The following core models have been extended to support Indian compliance:
- **Invoice**: Added `type`, `supplier`, `company`, and GST component fields (`cgst_amount`, `sgst_amount`, `igst_amount`).
- **CompanyProfile/Customer/Supplier**: Added `state_code` for GST locality matching.

### API Connections
Stubs for GSTN and IRP API interactions are available in `compliance/countries/in/gstn.py`.
