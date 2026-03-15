# Single-Country Configuration

Olive ERP is now optimized for a single-country configuration. The country is selected during the initial company setup and persists throughout the application.

## Key Changes
- **Single Country Focus**: All multi-country UI elements, including the country switcher, have been removed.
- **Dynamic Compliance Menu**: The sidebar now only displays compliance items relevant to the company's registered country.
- **Filtered API Endpoints**: Compliance APIs automatically filter data based on the company's `country_code`.
- **Simplified Dashboard**: The compliance dashboard is tailored to the specific regulations of the selected country.

## Configuration
The country is stored in the `CompanyProfile` model under the `country_code` field. This is set during Step 2 of the Setup Wizard.

### Supported Countries
- Ireland (IE)
- United Kingdom (GB)
- India (IN)
- United Arab Emirates (AE)

## Implementation Details
- `core/context_processors.py`: Handles the dynamic menu generation.
- `compliance/views.py`: Uses `CountryFilterMixin` to ensure country-specific access.
- `compliance/api.py`: Filters deadlines and filings by company country.
