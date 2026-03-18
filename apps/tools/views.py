import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus

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


_SCRAPE_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


def _scrape_product_page(url):
    """Fetch and parse competitor product page."""
    resp = requests.get(url, headers=_SCRAPE_HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    title_tag = soup.find('title')
    page_title = title_tag.get_text(strip=True) if title_tag else ''

    meta_desc = ''
    m = soup.find('meta', attrs={'name': 'description'})
    if m:
        meta_desc = m.get('content', '')

    og_title = ''
    og = soup.find('meta', attrs={'property': 'og:title'})
    if og:
        og_title = og.get('content', '')

    og_desc = ''
    ogd = soup.find('meta', attrs={'property': 'og:description'})
    if ogd:
        og_desc = ogd.get('content', '')

    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg', 'iframe']):
        tag.decompose()

    body_text = soup.get_text(separator='\n', strip=True)
    body_text = re.sub(r'\n{3,}', '\n\n', body_text)[:10000]

    return {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'og_title': og_title,
        'og_desc': og_desc,
        'body_text': body_text,
    }


def _scrape_amazon_reviews(brand_name, product_name):
    """Search Amazon for the product and pull real customer reviews."""
    try:
        query = f"{brand_name} {product_name}".strip()
        search_url = f"https://www.amazon.com/s?k={quote_plus(query)}"
        resp = requests.get(search_url, headers=_SCRAPE_HEADERS, timeout=12)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Find first product with an ASIN
        asin = None
        for el in soup.select('[data-asin]'):
            candidate = el.get('data-asin', '').strip()
            if candidate and len(candidate) == 10:
                asin = candidate
                break

        if not asin:
            return None

        reviews_url = (
            f"https://www.amazon.com/product-reviews/{asin}"
            f"?sortBy=recent&reviewerType=all_reviews&pageNumber=1"
        )
        resp2 = requests.get(reviews_url, headers=_SCRAPE_HEADERS, timeout=12)
        soup2 = BeautifulSoup(resp2.text, 'html.parser')

        reviews = []
        for rev in soup2.select('[data-hook="review"]')[:15]:
            body_el = rev.select_one('[data-hook="review-body"] span')
            rating_el = rev.select_one('[data-hook="review-star-rating"] span')
            title_el = rev.select_one('[data-hook="review-title"] span:last-child')
            if body_el and body_el.get_text(strip=True):
                reviews.append({
                    'body': body_el.get_text(strip=True)[:600],
                    'rating': rating_el.get_text(strip=True)[:5] if rating_el else '',
                    'title': title_el.get_text(strip=True) if title_el else '',
                })

        return {
            'asin': asin,
            'reviews': reviews,
            'product_url': f"https://www.amazon.com/dp/{asin}",
            'reviews_url': reviews_url,
        }
    except Exception:
        return None


def _scrape_reddit_voc(brand_name, product_category):
    """Pull Reddit discussions about the brand and product category."""
    try:
        reddit_headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; research-bot/1.0)',
            'Accept': 'application/json',
        }
        posts = []
        seen = set()

        for query in [brand_name, f"{product_category} review recommendation"]:
            if not query.strip():
                continue
            url = (
                f"https://www.reddit.com/search.json"
                f"?q={quote_plus(query)}&sort=top&limit=8&t=year&type=link"
            )
            resp = requests.get(url, headers=reddit_headers, timeout=10)
            if resp.status_code != 200:
                continue

            children = resp.json().get('data', {}).get('children', [])
            for child in children:
                d = child.get('data', {})
                pid = d.get('id', '')
                if pid in seen:
                    continue
                seen.add(pid)
                text = d.get('selftext', '').strip()
                title = d.get('title', '').strip()
                if len(text) < 30 and len(title) < 20:
                    continue
                posts.append({
                    'title': title,
                    'text': text[:700] if text else '',
                    'subreddit': d.get('subreddit', ''),
                    'score': d.get('score', 0),
                    'url': f"https://reddit.com{d.get('permalink', '')}",
                    'num_comments': d.get('num_comments', 0),
                })
                if len(posts) >= 8:
                    break
            if len(posts) >= 8:
                break

        return posts
    except Exception:
        return []


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

    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'AI analysis not configured'}, status=500)

    # Step 1: Scrape product page (needed to get brand/product names for other scrapers)
    try:
        page_data = _scrape_product_page(url)
    except requests.RequestException as e:
        return JsonResponse({'error': f'Could not fetch URL: {str(e)}'}, status=400)

    # Quick first-pass to extract brand/product name for parallel scrapers
    # Pull from og:title or page title
    raw_title = page_data['og_title'] or page_data['page_title'] or ''
    brand_guess = raw_title.split('|')[0].split('–')[0].split('-')[0].strip()[:60]
    product_guess = raw_title[:80]

    # Step 2: Parallel scrape Amazon + Reddit while we prep the prompt
    amazon_data = None
    reddit_data = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_amazon = executor.submit(_scrape_amazon_reviews, brand_guess, product_guess)
        future_reddit = executor.submit(_scrape_reddit_voc, brand_guess, brand_guess)

        try:
            amazon_data = future_amazon.result(timeout=20)
        except Exception:
            amazon_data = None

        try:
            reddit_data = future_reddit.result(timeout=15)
        except Exception:
            reddit_data = []

    # Step 3: Build enriched prompt with all data sources
    amazon_section = ''
    if amazon_data and amazon_data.get('reviews'):
        lines = [
            f"[{r['rating']}★] {r['title']}: {r['body']}"
            for r in amazon_data['reviews']
        ]
        amazon_section = '\n\nAMAZON CUSTOMER REVIEWS (real customer language — mine for exact phrases):\n'
        amazon_section += '\n---\n'.join(lines)[:4500]

    reddit_section = ''
    if reddit_data:
        lines = [
            f"r/{p['subreddit']} ({p['score']} upvotes, {p['num_comments']} comments)\n"
            f"Title: {p['title']}\n"
            f"{p['text'][:500]}"
            for p in reddit_data
        ]
        reddit_section = '\n\nREDDIT DISCUSSIONS (unfiltered community voice):\n'
        reddit_section += '\n---\n'.join(lines)[:3500]

    prompt = f"""You are a world-class DTC ad creative analyst. You have THREE data sources below — use ALL of them.

TARGET URL: {url}
Page Title: {page_data['page_title']}
OG Title: {page_data['og_title']}
Meta Description: {page_data['meta_desc']}

PRODUCT PAGE CONTENT:
{page_data['body_text']}
{amazon_section}
{reddit_section}

Synthesize ALL sources above into a structured intelligence report. The Amazon reviews and Reddit data contain REAL customer language — extract the exact phrases people use, their specific pain points, and transformation language. This is gold for ad copy.

Return ONLY a valid JSON object (no markdown, no extra text) with exactly these keys:

{{
  "brand_name": "string",
  "product_name": "string",
  "product_category": "string",
  "positioning_summary": "string — 2-3 sentences on their positioning and target customer",
  "price_point": "string — price if found, or 'Not listed'",
  "data_sources": {{
    "product_page": true,
    "amazon_reviews": {json.dumps(bool(amazon_data and amazon_data.get('reviews')))},
    "reddit_posts": {json.dumps(len(reddit_data))}
  }},
  "core_claims": ["top 5-7 claims they make about the product"],
  "target_avatars": [
    {{"avatar": "string", "pain_point": "string"}}
  ],
  "customer_voice": {{
    "top_complaints": ["3-5 most common complaints or frustrations from real reviews/reddit"],
    "top_praises": ["3-5 things customers love most — in their exact language"],
    "transformation_phrases": ["5-8 exact phrases customers use to describe before/after — word-for-word from the data"],
    "pain_language": ["5-8 specific pain point phrases customers actually use — not marketing language, real words"]
  }},
  "proven_angles": [
    {{
      "angle": "string",
      "hook_example": "string — a specific scroll-stopping hook using REAL customer language from the data above",
      "why_it_works": "string"
    }}
  ],
  "hook_ideas": ["5 specific scroll-stopping hook lines built from real customer language — not generic, pull actual phrases"],
  "ad_copy_language_bank": ["10-15 exact phrases, sentence fragments, or expressions from real customers to use directly in ad copy"],
  "content_gaps": ["angles they are NOT hitting that represent opportunities"],
  "positioning_vulnerabilities": ["weak points in their positioning you can attack"],
  "meta_ad_library_url": "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=BRAND_NAME_HERE"
}}"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model='claude-opus-4-6',
            max_tokens=3500,
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

    # Attach raw source URLs for the frontend
    if amazon_data:
        result['amazon_product_url'] = amazon_data.get('product_url', '')
        result['amazon_reviews_url'] = amazon_data.get('reviews_url', '')
        result['amazon_review_count'] = len(amazon_data.get('reviews', []))
    if reddit_data:
        result['reddit_posts'] = [
            {'title': p['title'], 'url': p['url'], 'subreddit': p['subreddit'], 'score': p['score']}
            for p in reddit_data[:6]
        ]

    return JsonResponse(result)
