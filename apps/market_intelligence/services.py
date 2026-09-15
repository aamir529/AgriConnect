import json
import logging
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import MarketBenchmarkPrice

logger = logging.getLogger(__name__)

DATA_GOV_IN_BASE_URL = 'https://api.data.gov.in/resource/'
DEFAULT_RESOURCE_ID = '9ef84268-d588-465a-a308-a864a43d0070'
SAMPLE_API_KEY = '579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b'

class MandiDataService:
    @classmethod
    def get_api_key(cls):
        return getattr(settings, 'DATA_GOV_IN_API_KEY', SAMPLE_API_KEY) or SAMPLE_API_KEY

    @classmethod
    def is_custom_key_configured(cls):
        key = getattr(settings, 'DATA_GOV_IN_API_KEY', '')
        return bool(key and key != SAMPLE_API_KEY)

    @classmethod
    def fetch_live_prices(cls, state=None, district=None, limit=50):
        """
        Fetches real-time APMC Mandi prices from Open Government Data (data.gov.in).
        Updates or creates MarketBenchmarkPrice records in the database.
        """
        api_key = cls.get_api_key()
        resource_id = getattr(settings, 'DATA_GOV_IN_MANDI_RESOURCE_ID', DEFAULT_RESOURCE_ID)
        
        query_params = {
            'api-key': api_key,
            'format': 'json',
            'limit': limit,
            'offset': 0,
        }
        if state:
            query_params['filters[state.keyword]'] = state
        if district:
            query_params['filters[district]'] = district

        full_url = f"{DATA_GOV_IN_BASE_URL}{resource_id}?{urllib.parse.urlencode(query_params)}"
        req = urllib.request.Request(
            full_url,
            headers={
                'User-Agent': 'AgriConnect-KisanSetu/1.0 (Indian Agriculture Mandi Integration)',
                'Accept': 'application/json'
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode('utf-8'))

            if 'error' in payload:
                error_msg = payload.get('error')
                return {
                    'success': False,
                    'is_rate_limited': 'rate limit' in str(error_msg).lower(),
                    'error': f"data.gov.in error: {error_msg}",
                    'count': 0,
                    'records': []
                }

            raw_records = payload.get('records', [])
            saved_count = 0
            processed_items = []

            for rec in raw_records:
                commodity = rec.get('commodity', '').strip()
                market = rec.get('market', '').strip()
                if not commodity or not market:
                    continue

                rec_state = rec.get('state', '').strip() or (state or 'India')
                rec_district = rec.get('district', '').strip() or (district or 'Local')
                mandi_name = f"{market} APMC Mandi" if 'mandi' not in market.lower() and 'apmc' not in market.lower() else market

                # Quintal to Kg conversion (1 Quintal = 100 Kg)
                try:
                    modal_raw = float(rec.get('modal_price') or 0)
                    min_raw = float(rec.get('min_price') or modal_raw)
                    max_raw = float(rec.get('max_price') or modal_raw)
                except (ValueError, TypeError):
                    continue

                if modal_raw <= 0:
                    continue

                modal_kg = Decimal(str(round(modal_raw / 100.0, 2)))
                min_kg = Decimal(str(round(min_raw / 100.0, 2)))
                max_kg = Decimal(str(round(max_raw / 100.0, 2)))
                # Retail supermarket estimated markup (~65% higher than wholesale APMC)
                retail_kg = Decimal(str(round(float(modal_kg) * 1.65, 2)))

                # Parse arrival date
                arrival_date_str = rec.get('arrival_date', '')
                rec_date = timezone.now().date()
                if arrival_date_str:
                    for date_fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
                        try:
                            rec_date = datetime.strptime(arrival_date_str, date_fmt).date()
                            break
                        except ValueError:
                            pass

                obj, created = MarketBenchmarkPrice.objects.update_or_create(
                    crop_name=commodity,
                    mandi_name=mandi_name,
                    defaults={
                        'district': rec_district,
                        'state': rec_state,
                        'modal_price_per_kg': modal_kg,
                        'min_price_per_kg': min_kg,
                        'max_price_per_kg': max_kg,
                        'retail_estimated_price_per_kg': retail_kg,
                        'recorded_date': rec_date,
                    }
                )
                saved_count += 1
                processed_items.append({
                    'crop': obj.crop_name,
                    'mandi': obj.mandi_name,
                    'modal_price': float(obj.modal_price_per_kg),
                    'retail_price': float(obj.retail_estimated_price_per_kg),
                    'state': obj.state,
                    'district': obj.district,
                    'date': str(obj.recorded_date),
                })

            return {
                'success': True,
                'source': 'data.gov.in (Agmarknet Live APMC Feed)',
                'count': saved_count,
                'records': processed_items,
                'is_rate_limited': False,
                'custom_key': cls.is_custom_key_configured()
            }

        except urllib.error.HTTPError as he:
            is_429 = (he.code == 429)
            msg = 'data.gov.in sample API key reached rate limit (HTTP 429). Please add your free personal API key in .env as DATA_GOV_IN_API_KEY.' if is_429 else f'HTTP {he.code}: {he.reason}'
            logger.warning('Mandi API HTTP Error: %s', msg)
            return {
                'success': False,
                'is_rate_limited': is_429,
                'error': msg,
                'count': 0
            }
        except Exception as e:
            logger.exception('Mandi API Fetch Error: %s', e)
            return {
                'success': False,
                'is_rate_limited': False,
                'error': str(e),
                'count': 0
            }

    @classmethod
    def seed_latest_market_data(cls):
        """
        Seeds or refreshes realistic benchmark rates with today's date
        as a reliable baseline when external network/keys are rate-limited.
        """
        today = timezone.now().date()
        benchmarks = [
            {'crop_name': 'Tomato (Hybrid Deshi)', 'mandi_name': 'Ranchi Pandra APMC Mandi', 'district': 'Ranchi', 'state': 'Jharkhand', 'modal': '24.50', 'min': '20.00', 'max': '28.00', 'retail': '44.00'},
            {'crop_name': 'Potato (Kufri Jyoti)', 'mandi_name': 'Ranchi Pandra APMC Mandi', 'district': 'Ranchi', 'state': 'Jharkhand', 'modal': '17.00', 'min': '14.00', 'max': '19.50', 'retail': '32.00'},
            {'crop_name': 'Onion (Nashik Red)', 'mandi_name': 'Ranchi Pandra APMC Mandi', 'district': 'Ranchi', 'state': 'Jharkhand', 'modal': '28.00', 'min': '24.00', 'max': '32.00', 'retail': '48.00'},
            {'crop_name': 'Green Chillies (Teja)', 'mandi_name': 'Ranchi Pandra APMC Mandi', 'district': 'Ranchi', 'state': 'Jharkhand', 'modal': '58.00', 'min': '48.00', 'max': '68.00', 'retail': '98.00'},
            {'crop_name': 'Cauliflower (Snowball)', 'mandi_name': 'Ramgarh District Mandi', 'district': 'Ramgarh', 'state': 'Jharkhand', 'modal': '26.00', 'min': '22.00', 'max': '30.00', 'retail': '48.00'},
            {'crop_name': 'Green Peas (Matar)', 'mandi_name': 'Hazaribagh APMC Market', 'district': 'Hazaribagh', 'state': 'Jharkhand', 'modal': '52.00', 'min': '45.00', 'max': '60.00', 'retail': '85.00'},
            {'crop_name': 'Cabbage (Golden Acre)', 'mandi_name': 'Ranchi Pandra APMC Mandi', 'district': 'Ranchi', 'state': 'Jharkhand', 'modal': '18.00', 'min': '15.00', 'max': '22.00', 'retail': '35.00'},
            {'crop_name': 'Ginger (Adrak Fresh)', 'mandi_name': 'Ranchi Pandra APMC Mandi', 'district': 'Ranchi', 'state': 'Jharkhand', 'modal': '95.00', 'min': '80.00', 'max': '110.00', 'retail': '160.00'},
            {'crop_name': 'Brinjal (Round Purple)', 'mandi_name': 'Bokaro Steel City APMC', 'district': 'Bokaro', 'state': 'Jharkhand', 'modal': '22.00', 'min': '18.00', 'max': '25.00', 'retail': '40.00'},
            {'crop_name': 'Pumpkin (Kaddu)', 'mandi_name': 'Dhanbad Krishi Bazar', 'district': 'Dhanbad', 'state': 'Jharkhand', 'modal': '14.00', 'min': '11.00', 'max': '17.00', 'retail': '26.00'},
        ]
        count = 0
        for b in benchmarks:
            MarketBenchmarkPrice.objects.update_or_create(
                crop_name=b['crop_name'],
                mandi_name=b['mandi_name'],
                defaults={
                    'district': b['district'],
                    'state': b['state'],
                    'modal_price_per_kg': Decimal(b['modal']),
                    'min_price_per_kg': Decimal(b['min']),
                    'max_price_per_kg': Decimal(b['max']),
                    'retail_estimated_price_per_kg': Decimal(b['retail']),
                    'recorded_date': today,
                }
            )
            count += 1
        return count