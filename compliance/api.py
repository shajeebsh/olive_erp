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
    """Get all compliance deadlines for calendar"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company = request.user.company
        country = request.GET.get('country', 'all')
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        events = []
        
        # Get deadlines from all active country engines
        for country_code in ['IE', 'GB', 'IN', 'AE']:
            if country != 'all' and country != country_code:
                continue
            
            engine = registry.get_compliance_engine(country_code)
            if not engine:
                continue
            
            deadlines = engine.get_filing_deadlines(company.id, date.today().year)
            for deadline in deadlines:
                events.append({
                    'id': f"{country_code}-{deadline['form']}",
                    'title': f"{country_code}: {deadline['name']}",
                    'start': deadline['due_date'],
                    'end': deadline['due_date'],
                    'description': deadline['description'],
                    'form': deadline['form'],
                    'country': country_code,
                })
        
        return Response(events)

class UpcomingDeadlinesView(APIView):
    """Get upcoming deadlines for next N days"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 7))
        company = request.user.company
        today = date.today()
        cutoff = today + timedelta(days=days)
        
        flags = {'IE': '🇮🇪', 'GB': '🇬🇧', 'IN': '🇮🇳', 'AE': '🇦🇪'}
        deadlines = []
        
        for country_code, flag in flags.items():
            engine = registry.get_compliance_engine(country_code)
            if not engine:
                continue
            
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
    """Get all pending filings"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company = request.user.company
        today = date.today()
        
        flags = {'IE': '🇮🇪', 'GB': '🇬🇧', 'IN': '🇮🇳', 'AE': '🇦🇪'}
        filings = []
        
        for country_code, flag in flags.items():
            engine = registry.get_compliance_engine(country_code)
            if not engine:
                continue
            
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
                elif days_until < 7:
                    status = 'due_soon'
                    status_text = '🟡 Due Soon'
                else:
                    status = 'pending'
                    status_text = '🟢 Pending'
                
                filings.append({
                    'id': period.id,
                    'country': country_code,
                    'country_flag': flag,
                    'form': period.form_type,
                    'period': f"{period.start_date} to {period.end_date}",
                    'due_date': period.due_date.isoformat(),
                    'status': status,
                    'status_text': status_text,
                })
        
        return Response(filings)
