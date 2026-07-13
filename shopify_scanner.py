import os
import random

class ShopifyScanner:
    """
    Scans online markets (mocking AliExpress hot-deals and hashtag engagement data)
    to extract the top 10 trending products based on high engagement and high supplier ratings.
    """
    def __init__(self):
        # We can configure mock data to perfectly match premium sports / adventure lifestyle brands (Nike, Nike-inspired, Adidas, North Face style)
        self.premium_catalogs = [
            {
                "title": "AeroSwift Breathe Performance Running Tee",
                "category": "Apparel",
                "base_price": 14.20,
                "orders": 12400,
                "rating": 4.8,
                "supplier": "PeakAthletics Co.",
                "images": ["https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500", "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=500"],
                "desc": "Engineered with zonal cooling zones and ultralight moisture-wicking weave. Designed for elite athletes pushing boundaries."
            },
            {
                "title": "VaporRidge Tech-Shell Waterproof Parka",
                "category": "Outwear",
                "base_price": 38.50,
                "orders": 8500,
                "rating": 4.9,
                "supplier": "ApexSupply Co.",
                "images": ["https://images.unsplash.com/photo-1548883354-7622d03aca27?w=500", "https://images.unsplash.com/photo-1508962914676-134849a727f0?w=500"],
                "desc": "Built with Triple-Dry breathable membrane technology. Fully taped seams with laser-cut ventilation underarms."
            },
            {
                "title": "AeroFlex Carbon-Fiber Running Shoes",
                "category": "Footwear",
                "base_price": 28.90,
                "orders": 18200,
                "rating": 4.7,
                "supplier": "Z-Speed Footwear",
                "images": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500", "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500"],
                "desc": "Propulsive carbon fiber flight plate coupled with responsive responsive energy-return cushioning. Run on clouds."
            },
            {
                "title": "ApexTrail Ergonomic Hydration Backpack",
                "category": "Gear",
                "base_price": 18.40,
                "orders": 6400,
                "rating": 4.8,
                "supplier": "OutBound Adventure",
                "images": ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500"],
                "desc": "Bounce-free fit suspension harness with rapid-access magnetic bites valve hydration hydration chamber."
            },
            {
                "title": "ThermalFit Core Compression Tights",
                "category": "Apparel",
                "base_price": 9.80,
                "orders": 11500,
                "rating": 4.6,
                "supplier": "PeakAthletics Co.",
                "images": ["https://images.unsplash.com/photo-1506152983158-b4a74a01c721?w=500"],
                "desc": "Dynamic gradient compression targets critical muscle zones, improving circulation and acceleration during intense efforts."
            },
            {
                "title": "HydroShield All-Weather Sports Duffel",
                "category": "Gear",
                "base_price": 16.50,
                "orders": 9200,
                "rating": 4.8,
                "supplier": "ApexSupply Co.",
                "images": ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500"],
                "desc": "IPX6 waterproof tarpaulin construction. Ergonomic stowable backpack straps with dual wet/dry isolation pockets."
            },
            {
                "title": "VoltPace Dual-Dial Fit Running Cap",
                "category": "Apparel",
                "base_price": 6.20,
                "orders": 4300,
                "rating": 4.7,
                "supplier": "CapMax Industries",
                "images": ["https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=500"],
                "desc": "Micro-adjustable tension wire closure delivers zero-point-fit precision. Reflective high-visibility safety graphics."
            },
            {
                "title": "EnduroMax Anti-Blister Compression Socks",
                "category": "Apparel",
                "base_price": 3.10,
                "orders": 24000,
                "rating": 4.9,
                "supplier": "PeakAthletics Co.",
                "images": ["https://images.unsplash.com/photo-1582966772680-860e372bb558?w=500"],
                "desc": "Engineered anatomically with Nanoflide fibers in key friction zones to eliminate hot-spots during extreme endurance efforts."
            },
            {
                "title": "ApexTrail Polarized Sport Sunglasses",
                "category": "Gear",
                "base_price": 11.80,
                "orders": 7900,
                "rating": 4.8,
                "supplier": "OutBound Adventure",
                "images": ["https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500"],
                "desc": "Impact-resistant shatterproof polycarbonate lenses. Smart hydrophobic frame design repels water and perspiration."
            },
            {
                "title": "AeroWeave Anti-Slip Gym Sweatband",
                "category": "Apparel",
                "base_price": 2.50,
                "orders": 31000,
                "rating": 4.7,
                "supplier": "PeakAthletics Co.",
                "images": ["https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500"],
                "desc": "Seamless breathable knit construction with interior medical-grade silicone grip channels."
            }
        ]

    def scan_trending_products(self, query: str = None, max_results: int = 10, margin_multiplier: float = 3.0) -> list:
        """
        Scans for trending sports and adventure dropshipping products.
        Returns product catalogs marked up with standard retail pricing structures.
        """
        results = []
        catalog = list(self.premium_catalogs)

        # Shuffle to simulate dynamic daily runs
        random.shuffle(catalog)

        # If a specific query exists, rank matching categories higher
        if query:
            q_lower = query.lower()
            catalog.sort(key=lambda x: (
                q_lower in x["title"].lower() or
                q_lower in x["category"].lower() or
                q_lower in x["desc"].lower()
            ), reverse=True)

        for idx, item in enumerate(catalog[:max_results]):
            retail_price = round(item["base_price"] * margin_multiplier, 2)
            results.append({
                "id": f"S22-PROD-{1000 + idx}",
                "title": item["title"],
                "category": item["category"],
                "cost_price": item["base_price"],
                "retail_price": retail_price,
                "profit": round(retail_price - item["base_price"], 2),
                "orders": item["orders"],
                "rating": item["rating"],
                "supplier": item["supplier"],
                "images": item["images"],
                "description": item["desc"],
                "source": "https://www.aliexpress.com"
            })

        print(f"[*] ShopifyScanner successfully loaded {len(results)} trending products matching query: '{query or 'All'}'")
        return results

if __name__ == "__main__":
    scanner = ShopifyScanner()
    trending = scanner.scan_trending_products(max_results=3)
    for p in trending:
        print(f"Product: {p['title']} | Cost: ${p['cost_price']} | Retail: ${p['retail_price']} | Rating: {p['rating']}")
