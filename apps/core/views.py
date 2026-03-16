from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    context = {
        'title': 'Reorderly — AI Supplier PO Agent for Shopify',
        'description': 'Reorderly monitors your Shopify inventory and automatically sends purchase orders to your suppliers when stock runs low. The AI-powered Stocky alternative.',
        'canonical': 'https://reorderly.com/',
        'og_image': 'https://reorderly.com/static/images/og-image.png',
    }
    return render(request, 'core/index.html', context)


def stocky_alternative(request):
    context = {
        'title': 'Best Stocky Alternative for Shopify (2026) — Reorderly',
        'description': 'Shopify discontinued Stocky in 2026. Reorderly is the AI-powered replacement — automated purchase orders, supplier management, and inventory reordering for Shopify merchants.',
        'canonical': 'https://reorderly.com/stocky-alternative/',
        'og_image': 'https://reorderly.com/static/images/og-image.png',
    }
    return render(request, 'core/stocky-alternative.html', context)


def pricing(request):
    context = {
        'title': 'Pricing — Reorderly AI Supplier PO Agent for Shopify',
        'description': 'Reorderly is free during early access. Paid plans starting at $99/month. No credit card required to get started.',
        'canonical': 'https://reorderly.com/pricing/',
        'og_image': 'https://reorderly.com/static/images/og-image.png',
    }
    return render(request, 'core/pricing.html', context)


def sitemap(request):
    urls = [
        {'loc': 'https://reorderly.com/', 'changefreq': 'weekly', 'priority': '1.0'},
        {'loc': 'https://reorderly.com/stocky-alternative/', 'changefreq': 'monthly', 'priority': '0.9'},
        {'loc': 'https://reorderly.com/pricing/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': 'https://reorderly.com/tools/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': 'https://reorderly.com/tools/po-email-generator/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': 'https://reorderly.com/tools/reorder-point-calculator/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': 'https://reorderly.com/tools/stockout-cost-calculator/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': 'https://reorderly.com/tools/days-of-supply-calculator/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': 'https://reorderly.com/tools/safety-stock-calculator/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': 'https://reorderly.com/tools/eoq-calculator/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': 'https://reorderly.com/tools/supplier-lead-time-tracker/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': 'https://reorderly.com/tools/moq-negotiation-email/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': 'https://reorderly.com/tools/stocky-migration-checklist/', 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': 'https://reorderly.com/tools/inventory-health-score/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': 'https://reorderly.com/resources/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': 'https://reorderly.com/resources/replacing-shopify-stocky/', 'changefreq': 'monthly', 'priority': '0.9'},
        {'loc': 'https://reorderly.com/resources/automate-purchase-orders-shopify/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': 'https://reorderly.com/resources/how-to-calculate-reorder-point/', 'changefreq': 'monthly', 'priority': '0.8'},
    ]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += '  <url>\n'
        xml += f'    <loc>{url["loc"]}</loc>\n'
        xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{url["priority"]}</priority>\n'
        xml += '  </url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')


def robots(request):
    content = """User-agent: *
Allow: /

Sitemap: https://reorderly.com/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')
