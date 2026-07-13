import unittest
from shopify_scanner import ShopifyScanner
from shopify_integrator import ShopifyIntegrator

class TestShopifyScanner(unittest.TestCase):
    def test_scan_trending_products(self):
        scanner = ShopifyScanner()
        # Scan with default params
        products = scanner.scan_trending_products(max_results=5)

        self.assertEqual(len(products), 5)
        for product in products:
            # Check for correct data model fields
            self.assertTrue(product["id"].startswith("S22-PROD-"))
            self.assertIn("title", product)
            self.assertIn("category", product)
            self.assertIn("cost_price", product)
            self.assertIn("retail_price", product)
            self.assertIn("images", product)
            self.assertIn("description", product)
            self.assertEqual(product["source"], "https://www.aliexpress.com")

    def test_pricing_markup_multiplier(self):
        scanner = ShopifyScanner()
        multiplier = 4.0
        products = scanner.scan_trending_products(max_results=1, margin_multiplier=multiplier)

        product = products[0]
        # Retail price should equal base_price multiplied by multiplier (rounded to 2 decimal places)
        expected_retail = round(product["cost_price"] * multiplier, 2)
        self.assertEqual(product["retail_price"], expected_retail)

class TestShopifyIntegrator(unittest.TestCase):
    def test_simulated_import(self):
        # Instantiate without environment variables to trigger mock dev/simulation mode
        integrator = ShopifyIntegrator(shop_name=None, access_token=None)

        test_product_data = {
            "id": "S22-PROD-1001",
            "title": "AeroSwift Breathe Performance Running Tee",
            "category": "Apparel",
            "cost_price": 14.20,
            "retail_price": 42.60,
            "description": "Premium sports wear compression top.",
            "supplier": "Elite Athletics Co.",
            "rating": 4.9,
            "images": ["https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500"]
        }

        result = integrator.import_product(test_product_data)

        # Verify simulated output payload structure matches requirements
        self.assertEqual(result["title"], "AeroSwift Breathe Performance Running Tee")
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["vendor"], "StagStudio22")
        self.assertEqual(result["product_type"], "Apparel")
        self.assertEqual(result["variants"][0]["price"], "42.6")
        self.assertEqual(result["variants"][0]["sku"], "S22-PROD-1001")
        self.assertEqual(len(result["images"]), 1)

if __name__ == "__main__":
    unittest.main()
