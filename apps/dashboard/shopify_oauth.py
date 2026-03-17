"""
Shopify OAuth 2.0 install + callback flow.
Handles the Shopify app installation and stores the access token.
"""
import hmac
import hashlib
import urllib.parse
import requests
import os
from django.conf import settings


SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_SCOPES = 'read_products,read_inventory,write_inventory,read_orders'
APP_URL = os.environ.get('APP_URL', 'https://reorderly.me')


def build_install_url(shop_domain: str, state: str) -> str:
    """Build the Shopify OAuth authorization URL."""
    redirect_uri = f"{APP_URL}/shopify/callback/"
    params = {
        'client_id': SHOPIFY_API_KEY,
        'scope': SHOPIFY_SCOPES,
        'redirect_uri': redirect_uri,
        'state': state,
        'grant_options[]': 'per-user',
    }
    query = urllib.parse.urlencode(params)
    return f"https://{shop_domain}/admin/oauth/authorize?{query}"


def verify_hmac(params: dict) -> bool:
    """Verify the HMAC signature from Shopify."""
    hmac_value = params.pop('hmac', '')
    sorted_params = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode('utf-8'),
        sorted_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(digest, hmac_value)


def exchange_token(shop_domain: str, code: str) -> str | None:
    """Exchange the auth code for a permanent access token."""
    url = f"https://{shop_domain}/admin/oauth/access_token"
    payload = {
        'client_id': SHOPIFY_API_KEY,
        'client_secret': SHOPIFY_API_SECRET,
        'code': code,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception:
        return None


def get_shop_info(shop_domain: str, access_token: str) -> dict:
    """Fetch basic shop info from Shopify."""
    url = f"https://{shop_domain}/admin/api/2024-01/shop.json"
    headers = {'X-Shopify-Access-Token': access_token}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get('shop', {})
    except Exception:
        return {}


def sync_products(shop_domain: str, access_token: str) -> list:
    """Fetch all products + variants + inventory from Shopify."""
    products = []
    url = f"https://{shop_domain}/admin/api/2024-01/products.json?limit=250&fields=id,title,variants"
    headers = {'X-Shopify-Access-Token': access_token}

    while url:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            products.extend(data.get('products', []))
            # Handle pagination via Link header
            link = response.headers.get('Link', '')
            url = None
            if 'rel="next"' in link:
                for part in link.split(','):
                    if 'rel="next"' in part:
                        url = part.split(';')[0].strip().strip('<>')
                        break
        except Exception:
            break

    return products


def get_inventory_levels(shop_domain: str, access_token: str, variant_ids: list) -> dict:
    """
    Fetch current inventory levels for a list of variant IDs.
    Returns {variant_id: quantity} dict.
    """
    if not variant_ids:
        return {}

    # First get inventory item IDs for the variants
    ids_str = ','.join(str(v) for v in variant_ids[:100])  # max 100 per request
    url = f"https://{shop_domain}/admin/api/2024-01/variants.json?ids={ids_str}&fields=id,inventory_item_id,inventory_quantity"
    headers = {'X-Shopify-Access-Token': access_token}

    result = {}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        for variant in response.json().get('variants', []):
            result[variant['id']] = variant.get('inventory_quantity', 0)
    except Exception:
        pass

    return result
