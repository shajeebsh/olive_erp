from wagtail.snippets.models import register_snippet
from tax_engine.countries.ie.models import Director, Secretary, Shareholder
from tax_engine.countries.ie.rbo import BeneficialOwner

register_snippet(Director)
register_snippet(Secretary)
register_snippet(Shareholder)
register_snippet(BeneficialOwner)
