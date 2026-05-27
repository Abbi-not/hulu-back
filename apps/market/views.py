"""
apps/market/views.py
────────────────────
GET /api/v1/market/                         → latest price per active commodity
GET /api/v1/market/?country=Ethiopia        → filtered by country
GET /api/v1/market/?commodity=Teff          → filtered by crop name (case-insensitive)
GET /api/v1/market/?market=Addis+Ababa      → filtered by market/region
GET /api/v1/market/?commodity=Teff&market=Hawassa  → combined

GET /api/v1/market/filters/                 → available commodities & markets for dropdowns
"""

from django.db.models import OuterRef, Subquery
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Commodity, MarketPrice
from .serializers import MarketPriceSerializer


# ── Seed data (used only when the DB has no prices yet) ───────────────────────
SEED_PRICES = [
    {"name": "Maize",   "price": 2450, "change": 120,  "unit": "per quintal", "icon": "🌽", "market": "Addis Ababa"},
    {"name": "Wheat",   "price": 3100, "change": 60,   "unit": "per quintal", "icon": "🌾", "market": "Addis Ababa"},
    {"name": "Teff",    "price": 5200, "change": -160, "unit": "per quintal", "icon": "🌿", "market": "Addis Ababa"},
    {"name": "Beans",   "price": 4800, "change": 50,   "unit": "per quintal", "icon": "🫘", "market": "Addis Ababa"},
    {"name": "Barley",  "price": 2100, "change": -42,  "unit": "per quintal", "icon": "🌱", "market": "Addis Ababa"},
    {"name": "Sorghum", "price": 1950, "change": 78,   "unit": "per quintal", "icon": "🌾", "market": "Addis Ababa"},
]

ALL_SEED_MARKETS = ["Addis Ababa", "Hawassa", "Dire Dawa", "Mekelle", "Bahir Dar", "Jimma"]


def _seed_response(commodity_filter="", market_filter=""):
    """Return seed prices with computed changePercent, optionally filtered."""
    items = []
    for s in SEED_PRICES:
        if commodity_filter and s["name"].lower() != commodity_filter.lower():
            continue
        if market_filter and s["market"].lower() != market_filter.lower():
            continue
        prev = s["price"] - s["change"]
        pct  = round(s["change"] / prev * 100, 2) if prev else 0
        items.append({
            "name":          s["name"],
            "unit":          s["unit"],
            "icon":          s["icon"],
            "price":         s["price"],
            "change":        s["change"],
            "changePercent": pct,
            "market":        s["market"],
            "country":       "Ethiopia",
            "recorded_at":   None,
            "source":        "seed",
        })
    return items


class MarketPriceListView(APIView):
    """
    Returns the latest price snapshot for every active commodity.

    Query params
    ─────────────
    country   – filter by country name (case-insensitive, optional)
    commodity – filter by crop name   (case-insensitive, optional)
    market    – filter by market/region (case-insensitive, optional)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        country   = request.query_params.get("country",   "").strip()
        commodity = request.query_params.get("commodity", "").strip()
        market    = request.query_params.get("market",    "").strip()

        # Sub-query: latest recorded_at per commodity, respecting all filters
        latest_qs = MarketPrice.objects.filter(commodity=OuterRef("commodity"))
        if country:
            latest_qs = latest_qs.filter(country__iexact=country)
        if market:
            latest_qs = latest_qs.filter(market__iexact=market)

        latest_qs = latest_qs.order_by("-recorded_at").values("id")[:1]

        prices_qs = (
            MarketPrice.objects
            .filter(id__in=Subquery(latest_qs))
            .select_related("commodity")
            .filter(commodity__is_active=True)
        )

        if commodity:
            prices_qs = prices_qs.filter(commodity__name__iexact=commodity)

        if not prices_qs.exists():
            return Response(_seed_response(commodity, market))

        serializer = MarketPriceSerializer(prices_qs, many=True)
        return Response(serializer.data)


class MarketFiltersView(APIView):
    """
    GET /api/v1/market/filters/

    Returns the list of available commodities and markets so the
    frontend can populate filter dropdowns without hardcoding values.

    Response shape:
    {
        "commodities": ["Barley", "Beans", "Maize", ...],
        "markets":     ["Addis Ababa", "Dire Dawa", ...]
    }
    """
    permission_classes = [AllowAny]

    def get(self, request):
        commodities = list(
            Commodity.objects.filter(is_active=True)
            .order_by("name")
            .values_list("name", flat=True)
        )
        markets = list(
            MarketPrice.objects
            .exclude(market="")
            .values_list("market", flat=True)
            .distinct()
            .order_by("market")
        )

        # Fall back to seed values if DB is empty
        if not commodities:
            commodities = sorted(s["name"] for s in SEED_PRICES)
        if not markets:
            markets = ALL_SEED_MARKETS

        return Response({"commodities": commodities, "markets": markets})
