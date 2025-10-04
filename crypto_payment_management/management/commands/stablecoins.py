from django.core.management.base import BaseCommand
from crypto_payment_management.models import Stablecoin


class Command(BaseCommand):
    help = "Seed supported stablecoins and major crypto assets for MVP"

    def handle(self, *args, **kwargs):
        stablecoins = [
            # Stablecoins
            {
                "name": "Tether USD",
                "symbol": "USDT",
                "blockchain": "Ethereum",
                "contract_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            },
            {
                "name": "USD Coin",
                "symbol": "USDC",
                "blockchain": "Ethereum",
                "contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            },
            {
                "name": "Dai Stablecoin",
                "symbol": "DAI",
                "blockchain": "Ethereum",
                "contract_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            },
            {
                "name": "Binance USD",
                "symbol": "BUSD",
                "blockchain": "Binance Smart Chain",
                "contract_address": "0xe9e7cea3dedca5984780bafc599bd69add087d56",
            },
            {
                "name": "TrueUSD",
                "symbol": "TUSD",
                "blockchain": "Ethereum",
                "contract_address": "0x0000000000085d4780B73119b644AE5ecd22b376",
            },

            # Major crypto assets (non-stable but widely used for payments)
            {
                "name": "Bitcoin",
                "symbol": "BTC",
                "blockchain": "Bitcoin",
                "contract_address": None,
            },
            {
                "name": "Ethereum",
                "symbol": "ETH",
                "blockchain": "Ethereum",
                "contract_address": None,
            },
            {
                "name": "Litecoin",
                "symbol": "LTC",
                "blockchain": "Litecoin",
                "contract_address": None,
            },
            {
                "name": "Bitcoin Cash",
                "symbol": "BCH",
                "blockchain": "Bitcoin Cash",
                "contract_address": None,
            },
            {
                "name": "Dogecoin",
                "symbol": "DOGE",
                "blockchain": "Dogecoin",
                "contract_address": None,
            },
            {
                "name": "TRON",
                "symbol": "TRX",
                "blockchain": "Tron",
                "contract_address": None,
            },
            {
                "name": "Ripple",
                "symbol": "XRP",
                "blockchain": "XRP Ledger",
                "contract_address": None,
            },
        ]

        for coin in stablecoins:
            obj, created = Stablecoin.objects.update_or_create(
                symbol=coin["symbol"], defaults=coin
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created new stablecoin: {coin['name']}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated stablecoin: {coin['name']}"))

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded stablecoins & major cryptos"))
