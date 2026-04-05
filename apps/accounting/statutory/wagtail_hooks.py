from wagtail.snippets.models import register_snippet
from compliance.countries.ie.models import Director, Secretary, Shareholder
from compliance.countries.ie.rbo import BeneficialOwner

register_snippet(Director)
register_snippet(Secretary)
register_snippet(Shareholder)
register_snippet(BeneficialOwner)
