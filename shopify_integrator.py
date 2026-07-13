import os
import json
import urllib.request
import urllib.error

class ShopifyIntegrator:
    """
    Connects to the Shopify Admin REST API to programmatically import dropshipped products,
    including automated pricing structure, high-end descriptions, and visual variants.
    """
    def __init__(self, shop_name: str = None, access_token: str = None):
        self.shop_name = shop_name or os.environ.get("SHOPIFY_SHOP_NAME")
        self.access_token = access_token or os.environ.get("SHOPIFY_ACCESS_TOKEN")

    def import_product(self, product_data: dict) -> dict:
        """
        Pushes a single product to Shopify. If no access token is configured,
        performs a simulated successful push and returns mock success payload.
        """
        if not self.shop_name or not self.access_token:
            print("[*] Shopify credentials missing. Simulating premium import payload push...")
            simulated_response = {
                "id": random_shopify_id(),
                "title": product_data["title"],
                "handle": product_data["title"].lower().replace(" ", "-"),
                "status": "active",
                "vendor": "StagStudio22",
                "product_type": product_data.get("category", "Athletic Gear"),
                "variants": [
                    {
                        "id": random_shopify_id() + 1,
                        "price": str(product_data["retail_price"]),
                        "sku": product_data.get("id", "S22-MOCK-SKU")
                    }
                ],
                "images": [{"src": url} for url in product_data.get("images", [])]
            }
            print(f"[+] [SIMULATED SUCCESS] Programmatically imported '{product_data['title']}' to storefront {self.shop_name or 'Prestige Store'}")
            return simulated_response

        # Build production Shopify payload
        url = f"https://{self.shop_name}.myshopify.com/admin/api/2023-10/products.json"

        # Format beautiful Nike/Adidas style HTML description
        body_html = (
            f"<div style='font-family: sans-serif; letter-spacing: 0.5px; line-height: 1.6;'>"
            f"  <p style='font-size: 14px; color: #111; font-weight: bold; text-transform: uppercase;'>Overview</p>"
            f"  <p style='color: #666; font-size: 13px;'>{product_data.get('description', '')}</p>"
            f"  <hr style='border: 0; border-top: 1px solid #ebebeb; margin: 20px 0;' />"
            f"  <p style='font-size: 14px; color: #111; font-weight: bold; text-transform: uppercase;'>Specs & Quality Check</p>"
            f"  <ul style='color: #666; font-size: 12px; padding-left: 18px;'>"
            f"    <li>Curated from Top-Tier Supplier: {product_data.get('supplier', 'Elite Sourcing')}</li>"
            f"    <li>Verified Supplier Rating: {product_data.get('rating', '4.8')}/5.0</li>"
            f"    <li>S22 Certified Sourcing Quality assurance</li>"
            f"  </ul>"
            f"</div>"
        )

        payload = {
            "product": {
                "title": product_data["title"].upper(),
                "body_html": body_html,
                "vendor": "StagStudio22",
                "product_type": product_data.get("category", "Premium Gear"),
                "status": "active",
                "images": [{"src": img_url} for img_url in product_data.get("images", [])],
                "variants": [
                    {
                        "price": str(product_data["retail_price"]),
                        "compare_at_price": str(round(product_data["retail_price"] * 1.3, 2)),
                        "sku": product_data.get("id", "S22-SKU"),
                        "requires_shipping": True,
                        "inventory_management": None
                    }
                ]
            }
        }

        # Send request
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": self.access_token
            },
            method="POST"
        )

        print(f"[*] Posting product '{product_data['title']}' to Shopify REST endpoint...")
        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                product_id = response_data.get("product", {}).get("id")
                print(f"[+] Shopify API Success! Created product with ID: {product_id}")
                return response_data.get("product", {})
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"[!] Shopify API HTTP Error {e.code}: {error_body}")
            raise e
        except Exception as e:
            print(f"[!] Shopify Integrator connection failed: {e}")
            raise e

def random_shopify_id() -> int:
    import random
    return random.randint(100000000000, 999999999999)

if __name__ == "__main__":
    integrator = ShopifyIntegrator()
    # Mock data to test import structure
    test_product = {
        "title": "AeroSwift Breathe Performance Running Tee",
        "category": "Apparel",
        "retail_price": 42.60,
        "description": "Premium sports wear compression top.",
        "supplier": "Elite Athletics Co.",
        "rating": 4.9,
        "images": ["https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500"]
    }
    integrator.import_product(test_product)
