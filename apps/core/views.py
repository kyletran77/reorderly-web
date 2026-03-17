from django.shortcuts import render
from django.http import HttpResponse

BASE_DOMAIN = 'https://reorderly.me'


def _waitlist_count():
    try:
        from apps.waitlist.models import WaitlistEntry
        real = WaitlistEntry.objects.count()
        return max(real + 312, 312)
    except Exception:
        return 312


def index(request):
    context = {
        'title': 'Reorderly — AI Supplier PO Agent for Shopify',
        'description': 'Reorderly monitors your Shopify inventory and automatically sends purchase orders to your suppliers when stock runs low. The AI-powered Stocky alternative.',
        'canonical': f'{BASE_DOMAIN}/',
        'og_image': f'{BASE_DOMAIN}/static/images/og-image.png',
        'waitlist_count': _waitlist_count(),
    }
    return render(request, 'core/index.html', context)


def stocky_alternative(request):
    context = {
        'title': 'Best Stocky Alternative for Shopify (2026) — Reorderly',
        'description': 'Shopify discontinued Stocky in 2026. Reorderly is the AI-powered replacement — automated purchase orders, supplier management, and inventory reordering for Shopify merchants.',
        'canonical': f'{BASE_DOMAIN}/stocky-alternative/',
        'og_image': f'{BASE_DOMAIN}/static/images/og-image.png',
        'waitlist_count': _waitlist_count(),
    }
    return render(request, 'core/stocky-alternative.html', context)


def pricing(request):
    context = {
        'title': 'Pricing — Reorderly AI Supplier PO Agent for Shopify',
        'description': 'Reorderly is free during early access. Paid plans starting at $149/month. No credit card required to get started.',
        'canonical': f'{BASE_DOMAIN}/pricing/',
        'og_image': f'{BASE_DOMAIN}/static/images/og-image.png',
        'waitlist_count': _waitlist_count(),
    }
    return render(request, 'core/pricing.html', context)


def privacy(request):
    context = {
        'title': 'Privacy Policy — Reorderly',
        'description': 'Reorderly Privacy Policy. How we collect, use, and protect your data.',
        'canonical': f'{BASE_DOMAIN}/privacy/',
    }
    return render(request, 'core/privacy.html', context)


def terms(request):
    context = {
        'title': 'Terms of Service — Reorderly',
        'description': 'Reorderly Terms of Service.',
        'canonical': f'{BASE_DOMAIN}/terms/',
    }
    return render(request, 'core/terms.html', context)


def sitemap(request):
    urls = [
        {'loc': f'{BASE_DOMAIN}/', 'changefreq': 'weekly', 'priority': '1.0'},
        {'loc': f'{BASE_DOMAIN}/stocky-alternative/', 'changefreq': 'monthly', 'priority': '0.9'},
        {'loc': f'{BASE_DOMAIN}/pricing/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': f'{BASE_DOMAIN}/directory/', 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': f'{BASE_DOMAIN}/directory/suppliers/', 'changefreq': 'weekly', 'priority': '0.8'},
        {'loc': f'{BASE_DOMAIN}/directory/stores/', 'changefreq': 'weekly', 'priority': '0.8'},
        {'loc': f'{BASE_DOMAIN}/privacy/', 'changefreq': 'yearly', 'priority': '0.3'},
        {'loc': f'{BASE_DOMAIN}/terms/', 'changefreq': 'yearly', 'priority': '0.3'},
    ]

    # Dynamically add all supplier and store detail pages
    try:
        from apps.directory.models import Supplier, ShopifyStore
        for supplier in Supplier.objects.only('slug').iterator():
            urls.append({
                'loc': f'{BASE_DOMAIN}/directory/suppliers/{supplier.slug}/',
                'changefreq': 'monthly',
                'priority': '0.7',
            })
        for store in ShopifyStore.objects.only('slug').iterator():
            urls.append({
                'loc': f'{BASE_DOMAIN}/directory/stores/{store.slug}/',
                'changefreq': 'monthly',
                'priority': '0.7',
            })
    except Exception:
        pass

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
    content = f"User-agent: *\nAllow: /\n\nSitemap: {BASE_DOMAIN}/sitemap.xml\n"
    return HttpResponse(content, content_type='text/plain')
