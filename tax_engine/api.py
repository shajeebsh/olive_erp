from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .registry import registry

class CountryListView(APIView):
    """List all available countries"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        countries = registry.get_all_countries()
        return Response(countries)

class TaxCalculationView(APIView):
    """Calculate tax for a given amount"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        country_code = request.data.get('country')
        amount = request.data.get('amount')
        tax_type = request.data.get('tax_type')

        engine = registry.get_tax_engine(country_code)
        if not engine:
            return Response({'error': 'Country not supported'}, status=400)

        result = engine.calculate_tax(amount, tax_type)
        return Response(result)

class TaxNumberValidationView(APIView):
    """Validate tax number format"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        country_code = request.data.get('country')
        tax_number = request.data.get('tax_number')

        is_valid, message = registry.validate_tax_number(country_code, tax_number)
        return Response({
            'is_valid': is_valid,
            'message': message
        })

from datetime import date, timedelta

class ComplianceDeadlinesView(APIView):
    """Get all compliance deadlines for calendar for the company's country"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company = request.user.company
        country = company.country_code
        
        engine = registry.get_compliance_engine(country)
        if not engine:
            return Response({'error': 'Country not configured'}, status=400)
            
        deadlines = engine.get_filing_deadlines(company.id, date.today().year)
        events = []
        for deadline in deadlines:
            events.append({
                'id': f"{country}-{deadline['form']}",
                'title': f"{country}: {deadline['name']}",
                'start': deadline['due_date'],
                'end': deadline['due_date'],
                'description': deadline['description'],
                'form': deadline['form'],
                'country': country,
            })
        
        return Response(events)

class UpcomingDeadlinesView(APIView):
    """Get upcoming deadlines for next N days for the company's country"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 7))
        company = request.user.company
        country = company.country_code
        today = date.today()
        cutoff = today + timedelta(days=days)
        
        engine = registry.get_compliance_engine(country)
        if not engine:
            return Response([])
            
        deadlines = []
        country_deadlines = engine.get_filing_deadlines(company.id, today.year)
        for dl in country_deadlines:
            due = date.fromisoformat(dl['due_date'])
            if today <= due <= cutoff:
                deadlines.append({
                    'country': country,
                    'form': dl['form'],
                    'description': dl['description'],
                    'due_date': dl['due_date'],
                    'days_until': (due - today).days,
                })
        
        deadlines.sort(key=lambda x: x['days_until'])
        return Response(deadlines)

class PendingFilingsView(APIView):
    """Get all pending filings for the company's country"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company = request.user.company
        country = company.country_code
        today = date.today()
        
        engine = registry.get_compliance_engine(country)
        if not engine:
            return Response([])
            
        from tax_engine.base.models import TaxPeriod
        periods = TaxPeriod.objects.filter(
            company=company,
            country=country,
            status__in=['open', 'in_progress']
        )
        
        filings = []
        for period in periods:
            days_until = (period.due_date - today).days
            if days_until < 0:
                status = 'overdue'
                status_text = '🔴 Overdue'
            elif days_until < 7:
                status = 'due_soon'
                status_text = '🟡 Due Soon'
            else:
                status = 'pending'
                status_text = '🟢 Pending'
            
            filings.append({
                'id': period.id,
                'country': country,
                'form': period.form_type,
                'period': f"{period.start_date} to {period.end_date}",
                'due_date': period.due_date.isoformat(),
                'status': status,
                'status_text': status_text,
            })
        
        return Response(filings)
