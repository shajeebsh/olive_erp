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
