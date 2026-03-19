from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Supplier, ShopifyStore, CATEGORY_CHOICES, COUNTRY_CHOICES

BASE = 'https://reorderly.com'


def directory_index(request):
    supplier_count = Supplier.objects.count()
    store_count = ShopifyStore.objects.count()
    featured_suppliers = Supplier.objects.filter(featured=True)[:6]
    featured_stores = ShopifyStore.objects.filter(featured=True)[:6]

    # Category breakdown for suppliers
    categories = []
    for code, label in CATEGORY_CHOICES:
        count = Supplier.objects.filter(category=code).count()
        if count > 0:
            categories.append({'code': code, 'label': label, 'count': count})

    return render(request, 'directory/index.html', {
        'title': 'DTC Store & Supplier Directory — Find Competitors to Analyze — Reorderly',
        'description': 'Browse top DTC Shopify stores by niche and verified overseas suppliers. Find your competitors, then run Ad Intel to mine their customer language and ship better ads.',
        'canonical': f'{BASE}/directory/',
        'supplier_count': supplier_count,
        'store_count': store_count,
        'featured_suppliers': featured_suppliers,
        'featured_stores': featured_stores,
        'categories': categories,
    })


def supplier_list(request):
    qs = Supplier.objects.all()

    # Filters
    category = request.GET.get('category', '')
    country = request.GET.get('country', '')
    q = request.GET.get('q', '').strip()

    if category:
        qs = qs.filter(category=category)
    if country:
        qs = qs.filter(country=country)
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(products__icontains=q) |
            Q(description__icontains=q) |
            Q(notable_brands__icontains=q)
        )

    total = qs.count()

    # Pagination — simple slice for now
    page = int(request.GET.get('page', 1))
    per_page = 24
    offset = (page - 1) * per_page
    suppliers = qs[offset:offset + per_page]
    has_next = total > offset + per_page

    # Build category counts for filters
    cat_counts = []
    for code, label in CATEGORY_CHOICES:
        count = Supplier.objects.filter(category=code).count()
        if count > 0:
            cat_counts.append({'code': code, 'label': label, 'count': count})

    countries_used = Supplier.objects.values_list('country', flat=True).distinct()
    country_options = [(c, n) for c, n in COUNTRY_CHOICES if c in countries_used]

    return render(request, 'directory/supplier_list.html', {
        'title': 'Shopify Supplier Directory — Find Verified Overseas Suppliers',
        'description': 'Browse suppliers used by top Shopify stores. Filter by product category and country of origin. Data from US customs import records.',
        'canonical': f'{BASE}/directory/suppliers/',
        'suppliers': suppliers,
        'total': total,
        'page': page,
        'has_next': has_next,
        'category_filter': category,
        'country_filter': country,
        'query': q,
        'cat_counts': cat_counts,
        'country_options': country_options,
    })


def supplier_detail(request, slug):
    supplier = get_object_or_404(Supplier, slug=slug)
    related = Supplier.objects.filter(category=supplier.category).exclude(pk=supplier.pk)[:4]

    return render(request, 'directory/supplier_detail.html', {
        'title': f'{supplier.name} — Shopify Supplier Profile | Reorderly',
        'description': f'{supplier.name} is a {supplier.country_name} supplier in {supplier.category_name}. See US import stats, notable brands, and how to automate POs with this supplier.',
        'canonical': f'{BASE}/directory/suppliers/{slug}/',
        'supplier': supplier,
        'related': related,
    })


def store_list(request):
    qs = ShopifyStore.objects.all()

    category = request.GET.get('category', '')
    revenue = request.GET.get('revenue', '')
    q = request.GET.get('q', '').strip()

    if category:
        qs = qs.filter(category=category)
    if revenue:
        qs = qs.filter(revenue_tier=revenue)
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(notable_for__icontains=q)
        )

    total = qs.count()
    page = int(request.GET.get('page', 1))
    per_page = 24
    offset = (page - 1) * per_page
    stores = qs[offset:offset + per_page]
    has_next = total > offset + per_page

    cat_counts = []
    for code, label in CATEGORY_CHOICES:
        count = ShopifyStore.objects.filter(category=code).count()
        if count > 0:
            cat_counts.append({'code': code, 'label': label, 'count': count})

    return render(request, 'directory/store_list.html', {
        'title': 'Top Shopify Stores by Category — Reorderly Directory',
        'description': 'Discover the best Shopify stores across every category. Browse by niche, revenue tier, and more.',
        'canonical': f'{BASE}/directory/stores/',
        'stores': stores,
        'total': total,
        'page': page,
        'has_next': has_next,
        'category_filter': category,
        'revenue_filter': revenue,
        'query': q,
        'cat_counts': cat_counts,
    })


def store_detail(request, slug):
    store = get_object_or_404(ShopifyStore, slug=slug)
    related = ShopifyStore.objects.filter(category=store.category).exclude(pk=store.pk)[:4]

    return render(request, 'directory/store_detail.html', {
        'title': f'{store.name} — Shopify Store Profile | Reorderly',
        'description': f'{store.name} is a {store.category_name} Shopify store. {store.description[:120] if store.description else ""}',
        'canonical': f'{BASE}/directory/stores/{slug}/',
        'store': store,
        'related': related,
    })
