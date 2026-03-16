from django.shortcuts import render

BASE = 'https://reorderly.com'


def content_index(request):
    articles = [
        {
            'title': 'Replacing Shopify Stocky Before August 31, 2026: Your Complete Guide',
            'slug': 'replacing-shopify-stocky',
            'description': 'Shopify Stocky shuts down August 31, 2026. Here\'s exactly what to export, what to look for in a replacement, and how to migrate without losing your reorder history.',
            'date': 'March 2026',
            'read_time': '8 min read',
            'tag': 'Migration Guide',
        },
        {
            'title': 'How to Automate Purchase Orders in Shopify (Without Hiring an Ops Manager)',
            'slug': 'automate-purchase-orders-shopify',
            'description': 'A practical guide to setting up automated PO emails for your Shopify store. Covers reorder thresholds, supplier setup, and what to look for in a PO automation tool.',
            'date': 'March 2026',
            'read_time': '6 min read',
            'tag': 'How-to Guide',
        },
        {
            'title': 'How to Calculate Reorder Point for Your Shopify Store (With Formula + Examples)',
            'slug': 'how-to-calculate-reorder-point',
            'description': 'Step-by-step guide to calculating reorder points for every SKU in your Shopify store. Includes the formula, real examples, and a free calculator.',
            'date': 'March 2026',
            'read_time': '7 min read',
            'tag': 'Inventory Guide',
        },
    ]
    return render(request, 'content/index.html', {
        'title': 'Shopify Inventory Guides — Reorderly',
        'description': 'Free guides for Shopify merchants on inventory management, purchase order automation, and replacing Shopify Stocky.',
        'canonical': f'{BASE}/resources/',
        'articles': articles,
    })


def replacing_stocky(request):
    return render(request, 'content/replacing_stocky.html', {
        'title': 'Replacing Shopify Stocky Before August 31, 2026: Your Complete Guide',
        'description': 'Shopify Stocky shuts down August 31, 2026. Here\'s exactly what to export, what to look for in a replacement, and how to migrate without losing your reorder history.',
        'canonical': f'{BASE}/resources/replacing-shopify-stocky/',
        'og_image': f'{BASE}/static/images/og-stocky.png',
    })


def automate_pos(request):
    return render(request, 'content/automate_pos.html', {
        'title': 'How to Automate Purchase Orders in Shopify (Without Hiring an Ops Manager)',
        'description': 'A practical guide to setting up automated PO emails for your Shopify store. Covers reorder thresholds, supplier setup, and what to look for in a PO automation tool.',
        'canonical': f'{BASE}/resources/automate-purchase-orders-shopify/',
    })


def reorder_point_guide(request):
    return render(request, 'content/reorder_point_guide.html', {
        'title': 'How to Calculate Reorder Point for Your Shopify Store (Formula + Examples)',
        'description': 'Step-by-step guide to calculating reorder points for every SKU. Includes the formula, real examples, and a free reorder point calculator.',
        'canonical': f'{BASE}/resources/how-to-calculate-reorder-point/',
    })
