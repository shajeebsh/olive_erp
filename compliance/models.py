import importlib
from .base.models import CountryConfig, TaxPeriod, TaxFiling, FilingApproval
from .countries.ie.models import Director, Secretary, Shareholder, OrdinaryShare, PreferenceShare
from .countries.ie.rbo import BeneficialOwner, RBORegistration

# UK Models
from .countries.uk.models import CompanyOfficer, ConfirmationStatement, PersonWithSignificantControl

# IN Models - Using importlib since 'in' is a reserved keyword
in_models = importlib.import_module('compliance.countries.in.models')
HSNCode = in_models.HSNCode
SACCode = in_models.SACCode
ProductTaxClassification = in_models.ProductTaxClassification

in_tds = importlib.import_module('compliance.countries.in.tds')
TDSSection = in_tds.TDSSection
TDSDeduction = in_tds.TDSDeduction
TDSChallan = in_tds.TDSChallan
TDSReturnQuarterly = in_tds.TDSReturnQuarterly

in_ewaybill = importlib.import_module('compliance.countries.in.ewaybill')
EWayBill = in_ewaybill.EWayBill
EWayBillItem = in_ewaybill.EWayBillItem

in_einvoice = importlib.import_module('compliance.countries.in.einvoice')
EInvoiceIRN = in_einvoice.EInvoiceIRN

# AE Models
from .countries.ae.excise import ExciseGoodsCategory, ExciseProduct, ExciseDeclaration, ExciseDeclarationLine
from .countries.ae.corporate_tax import CorporateTaxReturn, TaxLoss, FreeZonePerson

__all__ = [
    'CountryConfig',
    'TaxPeriod',
    'TaxFiling',
    'FilingApproval',
    'CompanyOfficer',
    'ConfirmationStatement',
    'PersonWithSignificantControl',
    'Director',
    'Secretary',
    'Shareholder',
    'OrdinaryShare',
    'PreferenceShare',
    'BeneficialOwner',
    'RBORegistration',
    'HSNCode',
    'SACCode',
    'ProductTaxClassification',
    'TDSSection',
    'TDSDeduction',
    'TDSChallan',
    'TDSReturnQuarterly',
    'EWayBill',
    'EWayBillItem',
    'EInvoiceIRN',
    'ExciseGoodsCategory',
    'ExciseProduct',
    'ExciseDeclaration',
    'ExciseDeclarationLine',
    'CorporateTaxReturn',
    'TaxLoss',
    'FreeZonePerson',
]
