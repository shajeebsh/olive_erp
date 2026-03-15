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
    """Get all compliance deadlines for calendar filtered by company country"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company = request.user.company
        if not company:
            from company.models import CompanyProfile
            company = CompanyProfile.objects.first()
            
        if not company or not company.country_code:
            return Response({'error': 'Country not configured'}, status=400)
            
        country = company.country_code
        engine = registry.get_compliance_engine(country)
        
        if not engine:
            return Response({'error': 'Compliance engine not found for country'}, status=400)
            
        deadlines = engine.get_filing_deadlines(company.id, date.today().year)
        events = []
        for deadline in deadlines:
            events.append({
                'id': f"{country}-{deadline['form']}",
                'title': deadline['name'],
                'start': deadline['due_date'],
                'end': deadline['due_date'],
                'description': deadline['description'],
                'form': deadline['form'],
                'country': country,
            })
        
        return Response(events)

class UpcomingDeadlinesView(APIView):
    """Get upcoming deadlines for user's company country only"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 7))
        company = request.user.company
        if not company:
            from company.models import CompanyProfile
            company = CompanyProfile.objects.first()
            
        if not company or not company.country_code:
            return Response([])
            
        today = date.today()
        cutoff = today + timedelta(days=days)
        country_code = company.country_code
        
        flags = {'IE': '🇮🇪', 'GB': '🇬🇧', 'IN': '🇮🇳', 'AE': '🇦🇪'}
        flag = flags.get(country_code, '🌍')
        
        engine = registry.get_compliance_engine(country_code)
        if not engine:
            return Response([])
            
        deadlines = []
        country_deadlines = engine.get_filing_deadlines(company.id, today.year)
        for dl in country_deadlines:
            due = date.fromisoformat(dl['due_date'])
            if today <= due <= cutoff:
                deadlines.append({
                    'country': country_code,
                    'country_flag': flag,
                    'form': dl['form'],
                    'description': dl['description'],
                    'due_date': dl['due_date'],
                    'days_until': (due - today).days,
                })
        
        # Sort by due date
        deadlines.sort(key=lambda x: x['days_until'])
        return Response(deadlines)

class PendingFilingsView(APIView):
    """Get pending filings for user's company country only"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company = request.user.company
        if not company:
            from company.models import CompanyProfile
            company = CompanyProfile.objects.first()
            
        if not company or not company.country_code:
            return Response([])
            
        today = date.today()
        country_code = company.country_code
        flags = {'IE': '🇮🇪', 'GB': '🇬🇧', 'IN': '🇮🇳', 'AE': '🇦🇪'}
        flag = flags.get(country_code, '🌍')
        
        filings = []
        # Get tax periods from company's compliance records
        from compliance.base.models import TaxPeriod
        periods = TaxPeriod.objects.filter(
            company=company,
            country=country_code,
            status__in=['open', 'in_progress']
        )
        
        for period in periods:
            days_until = (period.due_date - today).days
            if days_until < 0:
                status = 'overdue'
                status_text = '🔴 Overdue'
                status_color = 'danger'
            elif days_until < 7:
                status = 'due_soon'
                status_text = '🟡 Due Soon'
                status_color = 'warning'
            else:
                status = 'pending'
                status_text = '🟢 Pending'
                status_color = 'success'
            
            filings.append({
                'id': period.id,
                'country': country_code,
                'country_flag': flag,
                'form': period.form_type,
                'form_name': period.form_type, # Added for template compatibility
                'period': f"{period.start_date} to {period.end_date}",
                'due_date': period.due_date.isoformat(),
                'status': status_text,
                'status_color': status_color,
            })
        
        return Response(filings)
