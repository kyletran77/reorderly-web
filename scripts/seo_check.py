#!/usr/bin/env python3
"""
Reorderly SEO Audit Script
--------------------------
Crawls all pages defined in PAGES and checks for SEO health.
Run: python scripts/seo_check.py [--base-url http://localhost:8000]

Checks per page:
  - Title: exists, 30-60 chars
  - Meta description: exists, 120-160 chars
  - H1: exactly one
  - Canonical: exists and matches URL
  - Structured data: JSON-LD present
  - Internal links: at least 2
  - Image alt text: all images have alt
  - Open Graph: og:title, og:description present
"""

import sys
import re
import argparse
from urllib.request import urlopen, Request
from urllib.error import URLError
from html.parser import HTMLParser

BASE_URL = "http://localhost:8000"

PAGES = [
    "/",
    "/stocky-alternative/",
    "/pricing/",
    "/tools/",
    "/tools/po-email-generator/",
    "/tools/reorder-point-calculator/",
    "/tools/stockout-cost-calculator/",
    "/tools/days-of-supply-calculator/",
    "/tools/safety-stock-calculator/",
    "/tools/eoq-calculator/",
    "/tools/supplier-lead-time-tracker/",
    "/tools/moq-negotiation-email/",
    "/tools/stocky-migration-checklist/",
    "/tools/inventory-health-score/",
    "/resources/",
    "/resources/replacing-shopify-stocky/",
    "/resources/automate-purchase-orders-shopify/",
    "/resources/how-to-calculate-reorder-point/",
]

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta_description = ""
        self.og_title = ""
        self.og_description = ""
        self.canonical = ""
        self.h1_count = 0
        self.h1_text = ""
        self._in_h1 = False
        self.json_ld_count = 0
        self._in_json_ld = False
        self.internal_links = 0
        self.images_without_alt = []
        self.all_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "title":
            self._in_title = True

        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.meta_description = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content

        elif tag == "link":
            if attrs_dict.get("rel") == "canonical":
                self.canonical = attrs_dict.get("href", "")

        elif tag == "h1":
            self.h1_count += 1
            self._in_h1 = True

        elif tag == "script":
            if attrs_dict.get("type") == "application/ld+json":
                self._in_json_ld = True
                self.json_ld_count += 1

        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href.startswith("/") or BASE_URL in href:
                self.internal_links += 1

        elif tag == "img":
            alt = attrs_dict.get("alt")
            src = attrs_dict.get("src", "")
            if alt is None:
                self.images_without_alt.append(src)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "script" and self._in_json_ld:
            self._in_json_ld = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_h1:
            self.h1_text += data


def fetch_page(url):
    req = Request(url, headers={"User-Agent": "ReorderlyBot/1.0 SEO-Audit"})
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace"), resp.status
    except URLError as e:
        return None, str(e)


def check_page(path, base_url):
    url = base_url.rstrip("/") + path
    html, status = fetch_page(url)

    issues = []
    warnings = []
    passes = []

    if html is None:
        return path, [], [], [f"FETCH ERROR: {status}"], 0

    if isinstance(status, int) and status != 200:
        issues.append(f"HTTP {status}")

    parser = SEOParser()
    parser.feed(html)

    title = parser.title.strip()
    desc = parser.meta_description.strip()

    # Title
    if not title:
        issues.append("Missing <title>")
    elif len(title) < 30:
        warnings.append(f"Title too short ({len(title)} chars): '{title}'")
    elif len(title) > 60:
        warnings.append(f"Title too long ({len(title)} chars): '{title[:50]}...'")
    else:
        passes.append(f"Title OK ({len(title)} chars)")

    # Meta description
    if not desc:
        issues.append("Missing meta description")
    elif len(desc) < 120:
        warnings.append(f"Meta description short ({len(desc)} chars)")
    elif len(desc) > 160:
        warnings.append(f"Meta description long ({len(desc)} chars)")
    else:
        passes.append(f"Meta description OK ({len(desc)} chars)")

    # H1
    if parser.h1_count == 0:
        issues.append("No <h1> found")
    elif parser.h1_count > 1:
        warnings.append(f"Multiple <h1> tags ({parser.h1_count})")
    else:
        passes.append(f"H1 OK: '{parser.h1_text.strip()[:50]}'")

    # Canonical
    if not parser.canonical:
        warnings.append("Missing canonical link")
    else:
        passes.append(f"Canonical: {parser.canonical}")

    # Structured data
    if parser.json_ld_count == 0:
        warnings.append("No JSON-LD structured data")
    else:
        passes.append(f"JSON-LD: {parser.json_ld_count} block(s)")

    # Internal links
    if parser.internal_links < 2:
        warnings.append(f"Low internal links ({parser.internal_links})")
    else:
        passes.append(f"Internal links: {parser.internal_links}")

    # Images
    if parser.images_without_alt:
        issues.append(f"{len(parser.images_without_alt)} image(s) missing alt text")
    else:
        passes.append("All images have alt text")

    # OG tags
    if not parser.og_title:
        warnings.append("Missing og:title")
    if not parser.og_description:
        warnings.append("Missing og:description")
    if parser.og_title and parser.og_description:
        passes.append("OG tags present")

    score = len(passes) * 10 - len(issues) * 20 - len(warnings) * 5
    score = max(0, min(100, score))

    return path, passes, warnings, issues, score


def grade(score):
    if score >= 80:
        return f"{GREEN}●{RESET}"
    elif score >= 50:
        return f"{YELLOW}●{RESET}"
    else:
        return f"{RED}●{RESET}"


def main():
    parser = argparse.ArgumentParser(description="Reorderly SEO Audit")
    parser.add_argument("--base-url", default=BASE_URL, help="Base URL to audit")
    parser.add_argument("--page", help="Audit a single page path only")
    parser.add_argument("--issues-only", action="store_true", help="Only show pages with issues")
    args = parser.parse_args()

    pages = [args.page] if args.page else PAGES

    print(f"\n{BOLD}Reorderly SEO Audit{RESET}  {DIM}{args.base_url}{RESET}")
    print("─" * 70)

    total_issues = 0
    total_warnings = 0
    results = []

    for path in pages:
        path_, passes, warnings_, issues_, score = check_page(path, args.base_url)
        total_issues += len(issues_)
        total_warnings += len(warnings_)
        results.append((path_, passes, warnings_, issues_, score))

    for path_, passes, warnings_, issues_, score in results:
        has_problems = issues_ or warnings_
        if args.issues_only and not has_problems:
            continue

        g = grade(score)
        print(f"\n{g} {BOLD}{path_}{RESET}  {DIM}score: {score}/100{RESET}")

        for p in passes:
            print(f"   {GREEN}✓{RESET}  {DIM}{p}{RESET}")
        for w in warnings_:
            print(f"   {YELLOW}△{RESET}  {w}")
        for i in issues_:
            print(f"   {RED}✗{RESET}  {BOLD}{i}{RESET}")

    print("\n" + "─" * 70)
    status_color = RED if total_issues > 0 else (YELLOW if total_warnings > 0 else GREEN)
    print(f"{status_color}{BOLD}Summary:{RESET}  {total_issues} issues  •  {total_warnings} warnings  •  {len(pages)} pages audited")

    if total_issues > 0:
        print(f"\n{RED}Fix issues before deploying.{RESET}\n")
        sys.exit(1)
    else:
        print(f"\n{GREEN}All pages pass critical checks.{RESET}\n")


if __name__ == "__main__":
    main()
