from django.core.management.base import BaseCommand
from apps.market_intelligence.services import MandiDataService

class Command(BaseCommand):
    help = "Fetch real-time APMC Mandi commodity prices from data.gov.in (Agmarknet) or refresh benchmarks."

    def add_arguments(self, parser):
        parser.add_argument('--state', type=str, default=None, help='Filter by State (e.g. Jharkhand)')
        parser.add_argument('--district', type=str, default=None, help='Filter by District (e.g. Ranchi)')
        parser.add_argument('--limit', type=int, default=50, help='Max records to fetch from data.gov.in')
        parser.add_argument('--force-fallback', action='store_true', help='Force refresh with today\'s realistic benchmarks')

    def handle(self, *args, **options):
        state = options.get('state')
        district = options.get('district')
        limit = options.get('limit', 50)
        force_fallback = options.get('force_fallback')

        self.stdout.write(self.style.NOTICE("Connecting to Open Government Data (data.gov.in) Mandi API..."))

        if force_fallback:
            count = MandiDataService.seed_latest_market_data()
            self.stdout.write(self.style.SUCCESS(f"Successfully refreshed {count} benchmark commodities for today!"))
            return

        result = MandiDataService.fetch_live_prices(state=state, district=district, limit=limit)

        if result.get('success') and result.get('count', 0) > 0:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully synced {result['count']} live APMC mandi prices from data.gov.in!"
            ))
            for item in result.get('records', [])[:5]:
                self.stdout.write(f"  * {item['crop']} @ {item['mandi']} (Modal: Rs {item['modal_price']}/kg, Retail: Rs {item['retail_price']}/kg)")
            if result.get('count', 0) > 5:
                self.stdout.write(f"  ... and {result['count'] - 5} more.")
        else:
            err = result.get('error', 'Unknown issue')
            self.stdout.write(self.style.WARNING(f"Live API Notice: {err}"))
            self.stdout.write(self.style.NOTICE("Applying latest benchmark baseline to ensure up-to-date pricing..."))
            count = MandiDataService.seed_latest_market_data()
            self.stdout.write(self.style.SUCCESS(f"Refreshed {count} commodities for today's date."))