from django.shortcuts import render

BASE = 'https://reorderly.com'


def content_index(request):
    articles = [
        {
            'title': 'Shopify Stocky Shutdown: What Every Merchant Must Do Before August 31, 2026',
            'slug': 'shopify-stocky-shutdown',
            'description': 'Shopify removed Stocky from the App Store in February 2026 and will shut it down completely on August 31, 2026. Here\'s exactly what\'s happening and the steps to take right now.',
            'date': 'March 2026',
            'read_time': '6 min read',
            'tag': 'Urgent Guide',
        },
        {
            'title': 'Best Shopify Inventory Management Apps in 2026 (Honest Comparison)',
            'slug': 'best-shopify-inventory-apps',
            'description': 'With Stocky shutting down, hundreds of thousands of merchants need a replacement. We tested every major option — here\'s the honest breakdown of what each app actually does.',
            'date': 'March 2026',
            'read_time': '9 min read',
            'tag': "Buyer's Guide",
        },
        {
            'title': 'How to Send a Purchase Order to a Supplier in Shopify (2026)',
            'slug': 'shopify-purchase-order-supplier',
            'description': 'Shopify doesn\'t have a native way to email purchase orders to suppliers. Here\'s how to set up the full PO workflow — from creating orders to getting them to your suppliers automatically.',
            'date': 'March 2026',
            'read_time': '5 min read',
            'tag': 'How-to Guide',
        },
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


def stocky_shutdown(request):
    return render(request, 'content/shopify_stocky_shutdown.html', {
        'title': 'Shopify Stocky Shutdown: What Every Merchant Must Do Before August 31, 2026',
        'description': "Shopify removed Stocky from the App Store in February 2026 and will shut it down completely on August 31, 2026. Here's exactly what's happening and the steps to take right now.",
        'canonical': f'{BASE}/resources/shopify-stocky-shutdown/',
        'og_image': f'{BASE}/static/images/og-stocky.png',
    })


def best_inventory_apps(request):
    return render(request, 'content/best_shopify_inventory_apps.html', {
        'title': 'Best Shopify Inventory Management Apps in 2026 (Honest Comparison)',
        'description': "With Stocky shutting down, hundreds of thousands of merchants need a replacement. We tested every major option — here's the honest breakdown.",
        'canonical': f'{BASE}/resources/best-shopify-inventory-apps/',
    })


def shopify_po_supplier(request):
    return render(request, 'content/shopify_purchase_order_supplier.html', {
        'title': 'How to Send a Purchase Order to a Supplier in Shopify (2026)',
        'description': "Shopify doesn't have a native way to email purchase orders to suppliers. Here's how to set up the full PO workflow — from creating orders to sending them automatically.",
        'canonical': f'{BASE}/resources/shopify-purchase-order-supplier/',
    })
