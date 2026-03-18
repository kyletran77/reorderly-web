import json
import os
import re

import anthropic
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

BASE = 'https://reorderly.me'

TOOLS = [
    {
        'slug': 'po-email-generator',
        'name': 'PO Email Generator',
        'description': 'Generate a professional purchase order email to your supplier in 10 seconds. Free, no signup.',
        'icon': '📧',
        'url': '/tools/po-email-generator/',
    },
    {
        'slug': 'reorder-point-calculator',
        'name': 'Reorder Point Calculator',
        'description': 'Calculate the exact inventory level at which you should reorder each SKU.',
        'icon': '📊',
        'url': '/tools/reorder-point-calculator/',
    },
    {
        'slug': 'stockout-cost-calculator',
        'name': 'Stockout Cost Calculator',
        'description': 'Find out exactly how much stockouts are costing your store every month.',
        'icon': '💸',
        'url': '/tools/stockout-cost-calculator/',
    },
    {
        'slug': 'days-of-supply-calculator',
        'name': 'Days of Supply Calculator',
        'description': 'See how many days of stock you have left for any SKU before you run out.',
        'icon': '📅',
        'url': '/tools/days-of-supply-calculator/',
    },
    {
        'slug': 'safety-stock-calculator',
        'name': 'Safety Stock Calculator',
        'description': 'Calculate the right safety stock buffer to protect against demand spikes and supplier delays.',
        'icon': '🛡️',
        'url': '/tools/safety-stock-calculator/',
    },
    {
        'slug': 'eoq-calculator',
        'name': 'EOQ Calculator',
        'description': 'Find the optimal order quantity that minimizes your total inventory costs.',
        'icon': '⚖️',
        'url': '/tools/eoq-calculator/',
    },
    {
        'slug': 'supplier-lead-time-tracker',
        'name': 'Supplier Lead Time Tracker',
        'description': 'Track your suppliers\' actual vs. stated lead times and get a reliability score.',
        'icon': '⏱️',
        'url': '/tools/supplier-lead-time-tracker/',
    },
    {
        'slug': 'moq-negotiation-email',
        'name': 'MOQ Negotiation Email Generator',
        'description': 'Generate a professional email to negotiate minimum order quantities with your supplier.',
        'icon': '🤝',
        'url': '/tools/moq-negotiation-email/',
    },
    {
        'slug': 'stocky-migration-checklist',
        'name': 'Stocky Migration Checklist',
        'description': 'Shopify Stocky is shutting down Aug 31, 2026. Here\'s everything you need to do before then.',
        'icon': '✅',
        'url': '/tools/stocky-migration-checklist/',
    },
    {
        'slug': 'inventory-health-score',
        'name': 'Inventory Health Score',
        'description': 'Get a 0–100 score of your inventory health with specific recommendations to improve it.',
        'icon': '❤️',
        'url': '/tools/inventory-health-score/',
    },
]


def _ctx(title, description, slug, extra=None):
    ctx = {
        'title': title,
        'description': description,
        'canonical': f'{BASE}/tools/{slug}/' if slug else f'{BASE}/tools/',
        'tools': TOOLS,
    }
    if extra:
        ctx.update(extra)
    return ctx


def tools_index(request):
    return render(request, 'tools/index.html', _ctx(
        title='Free Shopify Inventory Tools — Reorderly',
        description='10 free tools for Shopify merchants: PO email generator, reorder point calculator, stockout cost calculator, safety stock calculator, and more.',
        slug=None,
    ))


def po_email_generator(request):
    return render(request, 'tools/po_email_generator.html', _ctx(
        title='Free Purchase Order Email Generator for Shopify — Reorderly',
        description='Generate a professional purchase order email to your supplier in seconds. Free, no signup required. Works for any Shopify merchant.',
        slug='po-email-generator',
    ))


def reorder_point_calculator(request):
    return render(request, 'tools/reorder_point_calculator.html', _ctx(
        title='Reorder Point Calculator for Shopify — Free Tool — Reorderly',
        description='Calculate the exact reorder point for any SKU. Enter your daily sales rate, supplier lead time, and safety stock to get your reorder point instantly.',
        slug='reorder-point-calculator',
    ))


def stockout_cost_calculator(request):
    return render(request, 'tools/stockout_cost_calculator.html', _ctx(
        title='Stockout Cost Calculator — How Much Are Stockouts Costing You? — Reorderly',
        description='Find out the real dollar cost of stockouts on your Shopify store. Enter your revenue and stockout frequency to see your annual loss.',
        slug='stockout-cost-calculator',
    ))


def days_of_supply_calculator(request):
    return render(request, 'tools/days_of_supply_calculator.html', _ctx(
        title='Days of Supply Calculator for Shopify — Free Tool — Reorderly',
        description='Calculate how many days of inventory you have left for any SKU. Instantly see green, yellow, or red status for your stock levels.',
        slug='days-of-supply-calculator',
    ))


def safety_stock_calculator(request):
    return render(request, 'tools/safety_stock_calculator.html', _ctx(
        title='Safety Stock Calculator for Ecommerce — Free Tool — Reorderly',
        description='Calculate the right safety stock level to protect against demand spikes and supplier delays. Free formula-based calculator for Shopify merchants.',
        slug='safety-stock-calculator',
    ))


def eoq_calculator(request):
    return render(request, 'tools/eoq_calculator.html', _ctx(
        title='EOQ Calculator — Economic Order Quantity for Shopify — Reorderly',
        description='Calculate the optimal order quantity that minimizes your total inventory costs. Free Economic Order Quantity calculator for ecommerce merchants.',
        slug='eoq-calculator',
    ))


def supplier_lead_time_tracker(request):
    return render(request, 'tools/supplier_lead_time_tracker.html', _ctx(
        title='Supplier Lead Time Tracker & Reliability Score — Free Tool — Reorderly',
        description='Track your suppliers\' actual vs. stated lead times. Get a reliability score for each supplier and know who you can trust.',
        slug='supplier-lead-time-tracker',
    ))


def moq_negotiation_email(request):
    return render(request, 'tools/moq_negotiation_email.html', _ctx(
        title='MOQ Negotiation Email Generator — Free Tool — Reorderly',
        description='Generate a professional email to negotiate minimum order quantities with your supplier. Free template generator for Shopify merchants.',
        slug='moq-negotiation-email',
    ))


def stocky_migration_checklist(request):
    return render(request, 'tools/stocky_migration_checklist.html', _ctx(
        title='Shopify Stocky Migration Checklist (Shutting Down Aug 2026) — Reorderly',
        description='Shopify Stocky is shutting down on August 31, 2026. Here\'s your complete migration checklist — what to export, what to find as a replacement, and how to migrate.',
        slug='stocky-migration-checklist',
    ))


def inventory_health_score(request):
    return render(request, 'tools/inventory_health_score.html', _ctx(
        title='Inventory Health Score — Free Shopify Inventory Audit — Reorderly',
        description='Get your Shopify store\'s inventory health score out of 100. Answer 8 questions and get a personalized report with specific recommendations.',
        slug='inventory-health-score',
    ))


def ad_intel(request):
    return render(request, 'tools/ad_intel.html', _ctx(
        title='Ad Intelligence Tool — Analyze Any Competitor\'s Ad Angles — Reorderly',
        description='Paste a competitor\'s product URL and instantly get a breakdown of their positioning, proven ad angles, hooks to steal, and content gaps to exploit.',
        slug='ad-intel',
    ))


@csrf_exempt
@require_POST
def api_ad_intel_analyze(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    url = data.get('url', '').strip()
    if not url:
        return JsonResponse({'error': 'URL is required'}, status=400)

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Scrape the competitor product page
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
    except requests.RequestException as e:
        return JsonResponse({'error': f'Could not fetch URL: {str(e)}'}, status=400)

    # Extract structured content from the page
    title_tag = soup.find('title')
    page_title = title_tag.get_text(strip=True) if title_tag else ''

    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag.get('content', '') if meta_desc_tag else ''

    og_title_tag = soup.find('meta', attrs={'property': 'og:title'})
    og_title = og_title_tag.get('content', '') if og_title_tag else ''

    og_desc_tag = soup.find('meta', attrs={'property': 'og:description'})
    og_desc = og_desc_tag.get('content', '') if og_desc_tag else ''

    # Remove script, style, nav, footer noise
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg', 'iframe']):
        tag.decompose()

    body_text = soup.get_text(separator='\n', strip=True)
    body_text = re.sub(r'\n{3,}', '\n\n', body_text)[:10000]

    # Claude analysis
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'AI analysis not configured'}, status=500)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an expert DTC ecommerce ad creative analyst with deep experience in Facebook/Instagram advertising. Analyze this competitor product page and return a structured intelligence report.

URL: {url}
Page Title: {page_title}
OG Title: {og_title}
Meta Description: {meta_desc}
OG Description: {og_desc}

Page Content (first 10,000 chars):
{body_text}

Return ONLY a valid JSON object (no markdown, no explanation) with exactly these keys:

{{
  "brand_name": "string — the brand name",
  "product_name": "string — the specific product name",
  "product_category": "string — e.g. skincare, supplements, fitness equipment",
  "positioning_summary": "string — 2-3 sentences on how they position this product and who it's for",
  "price_point": "string — price if found, or 'Not listed'",
  "core_claims": ["array of strings — top 5-7 specific claims they make about the product"],
  "target_avatars": [
    {{"avatar": "string", "pain_point": "string"}}
  ],
  "proven_angles": [
    {{
      "angle": "string — the ad angle name",
      "hook_example": "string — a specific example hook that would work for this angle",
      "why_it_works": "string — why this angle converts for this product"
    }}
  ],
  "hook_ideas": ["array of 5 specific scroll-stopping hook lines you could run against this product/niche"],
  "content_gaps": ["array of strings — angles they are NOT hitting that represent opportunities"],
  "positioning_vulnerabilities": ["array of strings — weak points in their positioning you can attack"],
  "meta_ad_library_url": "string — Facebook Ads Library search URL: https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=BRAND_NAME_HERE"
}}"""

    try:
        response = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=2500,
            messages=[{'role': 'user', 'content': prompt}],
        )
        result_text = response.content[0].text.strip()
        result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
        result_text = re.sub(r'\s*```$', '', result_text)
        result = json.loads(result_text)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'Failed to parse AI response: {str(e)}'}, status=500)
    except anthropic.APIError as e:
        return JsonResponse({'error': f'AI service error: {str(e)}'}, status=500)

    return JsonResponse(result)
