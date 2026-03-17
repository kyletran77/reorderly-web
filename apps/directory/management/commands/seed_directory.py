"""
Management command to seed the directory with supplier and store data.
Usage: python manage.py seed_directory [--clear]

Supplier data sourced from US customs import records (via Import Yeti).
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.directory.models import Supplier, ShopifyStore

COUNTRY_MAP = {
    'China': 'CN', 'Vietnam': 'VN', 'India': 'IN', 'Bangladesh': 'BD',
    'Taiwan': 'TW', 'South Korea': 'KR', 'Indonesia': 'ID', 'Pakistan': 'PK',
    'Turkey': 'TR', 'Mexico': 'MX', 'Italy': 'IT', 'Portugal': 'PT',
    'Cambodia': 'OTHER', 'Hong Kong': 'CN',
}

CAT_MAP = {
    'Apparel & Fashion': 'apparel', 'Home & Garden': 'home',
    'Beauty & Personal Care': 'beauty', 'Sports & Outdoors': 'sports',
    'Electronics & Accessories': 'electronics', 'Pet Supplies': 'pets',
    'Food & Beverage': 'food', 'Toys & Games': 'toys',
    'Health & Wellness': 'health',
}

# Real supplier data from US customs import records (Import Yeti)
SUPPLIERS = [
    # ── Apparel & Fashion ──────────────────────────────────────────
    {
        "name": "Dong Nam", "country": "Vietnam", "category": "Apparel & Fashion",
        "description": "High-volume Vietnamese activewear and athletic apparel manufacturer in Binh Duong Province, supplying major US DTC fitness and activewear brands.",
        "products": "Activewear, leggings, sports bras, athletic shorts",
        "us_importers": 12, "total_shipments": 1205, "annual_shipments": 200,
        "notable_brands": ["Fabletics"], "featured": True,
    },
    {
        "name": "King Hung Garments Industrial", "country": "Vietnam", "category": "Apparel & Fashion",
        "description": "Large-scale garment manufacturer in Ho Chi Minh City's Linh Trung Export Processing Zone, producing performance and lifestyle apparel for major US sporting goods brands.",
        "products": "Performance apparel, polo shirts, golf wear, lifestyle garments",
        "us_importers": 8, "total_shipments": 797, "annual_shipments": 133,
        "notable_brands": ["Cutter & Buck"], "featured": True,
    },
    {
        "name": "Nanjing Yiheda Textile", "country": "China", "category": "Apparel & Fashion",
        "description": "Major textile and apparel manufacturer based in Nanjing, China, supplying women's and men's clothing to mid-tier US fashion brands and apparel groups.",
        "products": "Women's fashion, men's clothing, knit garments",
        "us_importers": 4, "total_shipments": 433, "annual_shipments": 72,
        "notable_brands": ["Adjmi Apparel Group", "Boston Proper", "Planet Gold Clothing"], "featured": False,
    },
    {
        "name": "Nantong Fortune Fashion", "country": "China", "category": "Apparel & Fashion",
        "description": "Nantong, Jiangsu-based apparel manufacturer producing casual and contemporary clothing with 10 documented US customer relationships.",
        "products": "Casual wear, contemporary fashion, woven tops",
        "us_importers": 10, "total_shipments": 140, "annual_shipments": 23,
        "notable_brands": ["Civil Clothing"], "featured": False,
    },
    {
        "name": "Shaoxing Longwelltex", "country": "China", "category": "Apparel & Fashion",
        "description": "Textile and garment manufacturer located in Shaoxing, Zhejiang — one of China's major textile hubs — producing fabrics and finished apparel.",
        "products": "Fabrics, finished garments, woven textiles",
        "us_importers": 5, "total_shipments": 180, "annual_shipments": 30,
        "notable_brands": ["Minx International"], "featured": False,
    },
    {
        "name": "Pinghu Diya Garments", "country": "China", "category": "Apparel & Fashion",
        "description": "Zhejiang-based garment and accessories factory supplying the popular Canadian lifestyle brand Herschel Supply Co.",
        "products": "Bags, accessories, soft goods, apparel",
        "us_importers": 4, "total_shipments": 46, "annual_shipments": 8,
        "notable_brands": ["Herschel Supply"], "featured": True,
    },
    {
        "name": "Vicmark Fashions Cambodia", "country": "Cambodia", "category": "Apparel & Fashion",
        "description": "Cambodian garment manufacturer producing men's and women's swimwear, outerwear, and woven apparel for US premium lifestyle brands.",
        "products": "Swimwear, outerwear, woven apparel, resort wear",
        "us_importers": 2, "total_shipments": 32, "annual_shipments": 5,
        "notable_brands": ["Faherty Brand"], "featured": True,
    },
    {
        "name": "Yotex Apparel Shanghai", "country": "China", "category": "Apparel & Fashion",
        "description": "Shanghai-based sportswear and activewear manufacturer specializing in yoga wear and athletic apparel for US DTC brands.",
        "products": "Yoga wear, activewear, performance clothing",
        "us_importers": 3, "total_shipments": 62, "annual_shipments": 10,
        "notable_brands": ["Set Active"], "featured": True,
    },
    {
        "name": "J & J Fashion", "country": "Vietnam", "category": "Apparel & Fashion",
        "description": "Vietnam-based garment manufacturer in the Long Hau Industrial Zone, producing casual and contemporary fashion apparel for US buyers.",
        "products": "Casual wear, contemporary fashion, cut-and-sew",
        "us_importers": 5, "total_shipments": 85, "annual_shipments": 14,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Youngones Bangladesh", "country": "Bangladesh", "category": "Apparel & Fashion",
        "description": "Bangladeshi garment manufacturer producing basics and essentials for global fashion and value retailers.",
        "products": "Basic tees, essentials, knit garments, casual wear",
        "us_importers": 3, "total_shipments": 3, "annual_shipments": 1,
        "notable_brands": ["Uniqlo USA"], "featured": False,
    },
    # ── Home & Garden ──────────────────────────────────────────────
    {
        "name": "UE Furniture", "country": "China", "category": "Home & Garden",
        "description": "Massive furniture manufacturer in Anji, Huzhou — one of China's furniture manufacturing capitals — with over 15,600 shipments on record as a primary supplier to IKEA.",
        "products": "Sofas, chairs, bedroom furniture, living room sets",
        "us_importers": 35, "total_shipments": 15629, "annual_shipments": 2604,
        "notable_brands": ["IKEA Supply"], "featured": True,
    },
    {
        "name": "Htctech", "country": "Vietnam", "category": "Home & Garden",
        "description": "Ha Nam Province, Vietnam manufacturer and primary supplier to Scrub Daddy — the viral Shark Tank cleaning brand — producing Scrub Daddy sponge products and cleaning accessories.",
        "products": "Cleaning sponges, scrubbers, household cleaning accessories",
        "us_importers": 6, "total_shipments": 287, "annual_shipments": 48,
        "notable_brands": ["Scrub Daddy"], "featured": True,
    },
    {
        "name": "Huisen Furniture Longnan", "country": "China", "category": "Home & Garden",
        "description": "One of China's highest-volume furniture exporters based in Ganzhou, Jiangxi Province, producing home furniture including sofas, chairs, and bedroom sets.",
        "products": "Sofas, chairs, bedroom sets, upholstered furniture",
        "us_importers": 15, "total_shipments": 1517, "annual_shipments": 253,
        "notable_brands": ["Zenith Home"], "featured": True,
    },
    {
        "name": "Jiangsu Acome Outdoor Products", "country": "China", "category": "Home & Garden",
        "description": "Yangzhou, Jiangsu manufacturer of outdoor and garden products including furniture, garden accessories, and outdoor equipment.",
        "products": "Outdoor furniture, garden accessories, patio sets",
        "us_importers": 8, "total_shipments": 584, "annual_shipments": 97,
        "notable_brands": ["Supra Distribution"], "featured": False,
    },
    {
        "name": "Youngsang International", "country": "China", "category": "Home & Garden",
        "description": "Shanghai-based home goods and textile manufacturer producing bedding, bath, and decorative items for US home furnishing brands.",
        "products": "Bedding, bath textiles, decorative pillows, throws",
        "us_importers": 12, "total_shipments": 385, "annual_shipments": 64,
        "notable_brands": ["Cotton And Blue"], "featured": False,
    },
    {
        "name": "Jiang Su Chairone Home Furniture", "country": "China", "category": "Home & Garden",
        "description": "Siyang, Jiangsu-based furniture manufacturer producing upholstered seating and home furniture with consistent shipping activity.",
        "products": "Upholstered chairs, sofas, dining chairs",
        "us_importers": 20, "total_shipments": 359, "annual_shipments": 60,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Anji Baishengju Furniture", "country": "China", "category": "Home & Garden",
        "description": "Anji Economic Development Zone, Zhejiang furniture manufacturer producing bamboo and eco-friendly home furniture in China's premier green furniture district.",
        "products": "Bamboo furniture, eco-friendly home furnishings, chairs",
        "us_importers": 4, "total_shipments": 85, "annual_shipments": 14,
        "notable_brands": ["Bakam"], "featured": False,
    },
    {
        "name": "Hangzhou M&M Home Textile", "country": "China", "category": "Home & Garden",
        "description": "Hangzhou, Zhejiang manufacturer producing cushions, pillows, mattresses, and home textiles for US bedroom and home decor brands.",
        "products": "Cushions, pillows, mattresses, bedskirts, home textiles",
        "us_importers": 6, "total_shipments": 110, "annual_shipments": 18,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Jiangsu Green Full Garden Products", "country": "China", "category": "Home & Garden",
        "description": "Changzhou, Jiangsu manufacturer of garden netting, bird mesh, shade cloth, and protective mesh products for garden and agricultural use.",
        "products": "Garden netting, shade cloth, bird mesh, windscreen",
        "us_importers": 6, "total_shipments": 47, "annual_shipments": 8,
        "notable_brands": ["Beyond Broadway"], "featured": False,
    },
    {
        "name": "HTJ Trade", "country": "China", "category": "Home & Garden",
        "description": "Hong Kong-based trade company handling metal candle holders, porcelain, pottery, and home accessories for US gift and home decor importers.",
        "products": "Candle holders, porcelain, pottery, houseware, home accessories",
        "us_importers": 5, "total_shipments": 33, "annual_shipments": 6,
        "notable_brands": ["Dynasty Gift"], "featured": False,
    },
    {
        "name": "Weihai Dafang Outdoors Product", "country": "China", "category": "Home & Garden",
        "description": "Weihai, China outdoor product manufacturer supplying garden furniture, outdoor accessories, and seasonal products to US specialty retailers.",
        "products": "Garden furniture, outdoor accessories, seasonal decor",
        "us_importers": 4, "total_shipments": 33, "annual_shipments": 6,
        "notable_brands": ["Stage"], "featured": False,
    },
    # ── Beauty & Personal Care ─────────────────────────────────────
    {
        "name": "A&H International Cosmetic", "country": "China", "category": "Beauty & Personal Care",
        "description": "Fengxian District, Shanghai cosmetics manufacturer supplying major US beauty brands including Morphe, with one of the highest shipment volumes in the beauty category.",
        "products": "Eyeshadow palettes, pressed powders, lip products, face makeup",
        "us_importers": 15, "total_shipments": 1549, "annual_shipments": 258,
        "notable_brands": ["Morphe"], "featured": True,
    },
    {
        "name": "Pingdu Heart Girl Eyelash Factory", "country": "China", "category": "Beauty & Personal Care",
        "description": "Qingdao-based false eyelash specialist with over 20 years experience, producing 12 million pairs annually for US beauty brands.",
        "products": "False eyelashes, lash strips, lash accessories",
        "us_importers": 7, "total_shipments": 405, "annual_shipments": 68,
        "notable_brands": ["Moira Cosmetics", "Kara Beauty"], "featured": True,
    },
    {
        "name": "Zhongshan Meiyuan Cosmetics", "country": "China", "category": "Beauty & Personal Care",
        "description": "Zhongshan, Guangdong cosmetics manufacturer producing a wide range of beauty products with consistent exports to US importers.",
        "products": "Skincare, color cosmetics, personal care, beauty tools",
        "us_importers": 7, "total_shipments": 318, "annual_shipments": 53,
        "notable_brands": ["Michael Giordano International"], "featured": False,
    },
    {
        "name": "Foshan Bomacy Beauty Equipment", "country": "China", "category": "Beauty & Personal Care",
        "description": "Shunde District, Foshan manufacturer of beauty equipment and personal care devices with active exports to US beauty supply and discount retailers.",
        "products": "Beauty devices, personal care electronics, hair tools, skin care tools",
        "us_importers": 8, "total_shipments": 153, "annual_shipments": 26,
        "notable_brands": ["AP Discount"], "featured": False,
    },
    {
        "name": "Eshine Star Hair Beauty Products", "country": "China", "category": "Beauty & Personal Care",
        "description": "Guangzhou hair care products manufacturer producing professional and consumer hair tools, extensions, and styling accessories.",
        "products": "Hair tools, extensions, styling accessories, professional equipment",
        "us_importers": 4, "total_shipments": 94, "annual_shipments": 16,
        "notable_brands": ["H2Pro Beauty Life"], "featured": False,
    },
    {
        "name": "Yiwu Manyan Cosmetics", "country": "China", "category": "Beauty & Personal Care",
        "description": "Yiwu, Zhejiang cosmetics manufacturer producing affordable beauty and personal care products including makeup and beauty accessories.",
        "products": "Makeup, skincare, beauty accessories, personal care",
        "us_importers": 6, "total_shipments": 120, "annual_shipments": 20,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Inox World Industries", "country": "India", "category": "Beauty & Personal Care",
        "description": "Kundli Industrial Estate, Sonepat manufacturer producing personal care and household products for major US value retail chains.",
        "products": "Personal care products, household items, value retail goods",
        "us_importers": 5, "total_shipments": 40, "annual_shipments": 7,
        "notable_brands": ["Dolgencorp (Dollar General)"], "featured": False,
    },
    {
        "name": "Rateria International", "country": "India", "category": "Beauty & Personal Care",
        "description": "Noida, Uttar Pradesh manufacturer and exporter of personal care products, cosmetics accessories, and beauty goods.",
        "products": "Personal care accessories, cosmetic tools, beauty goods",
        "us_importers": 4, "total_shipments": 93, "annual_shipments": 16,
        "notable_brands": ["E&E"], "featured": False,
    },
    {
        "name": "Harmony Beauty International", "country": "China", "category": "Beauty & Personal Care",
        "description": "Shanghai-based beauty trading company specializing in skincare, color cosmetics, and personal care items for US brand importers.",
        "products": "Skincare, color cosmetics, personal care",
        "us_importers": 5, "total_shipments": 95, "annual_shipments": 16,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Guangzhou Huashi Cosmetics Technology", "country": "China", "category": "Beauty & Personal Care",
        "description": "Huadu District, Guangzhou cosmetics technology company producing personal care and cosmetic formulations for US beauty brands.",
        "products": "Cosmetic formulations, skincare, private label beauty",
        "us_importers": 3, "total_shipments": 4, "annual_shipments": 1,
        "notable_brands": ["Modern Beauty"], "featured": False,
    },
    # ── Sports & Outdoors ──────────────────────────────────────────
    {
        "name": "Qingdao Wintrak Outdoor Equipment", "country": "China", "category": "Sports & Outdoors",
        "description": "Qingdao manufacturer of hammocks, camping gear, and outdoor recreational equipment, supplying US outdoor lifestyle brands.",
        "products": "Hammocks, camping gear, outdoor accessories, tents",
        "us_importers": 5, "total_shipments": 58, "annual_shipments": 10,
        "notable_brands": ["Grand Trunk"], "featured": True,
    },
    {
        "name": "Unicorn Recreation Products", "country": "China", "category": "Sports & Outdoors",
        "description": "Tianjin-based outdoor recreation product manufacturer producing camping, hiking, and outdoor lifestyle accessories for US brands.",
        "products": "Camping accessories, hiking gear, outdoor lifestyle products",
        "us_importers": 10, "total_shipments": 138, "annual_shipments": 23,
        "notable_brands": ["Equip Outdoor Technologies"], "featured": False,
    },
    {
        "name": "Sportlux Enterprise", "country": "Taiwan", "category": "Sports & Outdoors",
        "description": "Taipei-based sports equipment manufacturer producing rackets, balls, and recreational sports goods for US distributors.",
        "products": "Rackets, balls, recreational sports goods, sporting accessories",
        "us_importers": 8, "total_shipments": 156, "annual_shipments": 26,
        "notable_brands": ["Indian Industries"], "featured": False,
    },
    {
        "name": "Mastercraft Boxing and Fitness Equipment", "country": "China", "category": "Sports & Outdoors",
        "description": "Hong Kong-based sporting goods company manufacturing boxing gloves, pads, training equipment, and martial arts gear.",
        "products": "Boxing gloves, pads, MMA gear, martial arts equipment",
        "us_importers": 4, "total_shipments": 16, "annual_shipments": 3,
        "notable_brands": ["Fuji Mats"], "featured": False,
    },
    {
        "name": "Shandong Land Fitness Tech", "country": "China", "category": "Sports & Outdoors",
        "description": "Shandong Province fitness equipment manufacturer producing commercial and consumer exercise machines, weights, and fitness accessories.",
        "products": "Exercise machines, weights, fitness accessories, gym equipment",
        "us_importers": 6, "total_shipments": 75, "annual_shipments": 13,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Guangdong Freeman Outdoor", "country": "China", "category": "Sports & Outdoors",
        "description": "Dongguan, Guangdong outdoor equipment manufacturer producing power tools, outdoor accessories, and recreational equipment.",
        "products": "Power tools, outdoor accessories, recreational equipment",
        "us_importers": 5, "total_shipments": 30, "annual_shipments": 5,
        "notable_brands": ["Evolution Power Tools"], "featured": False,
    },
    {
        "name": "Guang Zhou Kaipun Sports", "country": "China", "category": "Sports & Outdoors",
        "description": "Zengcheng City, Guangdong sports goods manufacturer producing balls, rackets, and recreational sports equipment for US mid-market brands.",
        "products": "Sports balls, rackets, recreational equipment",
        "us_importers": 3, "total_shipments": 8, "annual_shipments": 1,
        "notable_brands": ["Baden Sports"], "featured": False,
    },
    {
        "name": "Nantong Better Sports and Fitness", "country": "China", "category": "Sports & Outdoors",
        "description": "Nantong-based sports and fitness equipment manufacturer supplying value-oriented fitness goods to large US grocery and discount retailers.",
        "products": "Fitness equipment, sports accessories, value fitness goods",
        "us_importers": 3, "total_shipments": 6, "annual_shipments": 1,
        "notable_brands": ["Aldi"], "featured": False,
    },
    {
        "name": "Yiwu Zhiqu Sports Fitness Equipment", "country": "China", "category": "Sports & Outdoors",
        "description": "Beiyuan Industry, Yiwu fitness equipment manufacturer producing small fitness accessories and exercise equipment for US commercial buyers.",
        "products": "Resistance bands, fitness accessories, small gym equipment",
        "us_importers": 3, "total_shipments": 11, "annual_shipments": 2,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Cangzhou Shuangdie Sports Equipment", "country": "China", "category": "Sports & Outdoors",
        "description": "Hebei Province sports equipment manufacturer based in a dedicated sports industrial park, producing outdoor and recreational sporting goods.",
        "products": "Outdoor sporting goods, recreational equipment",
        "us_importers": 2, "total_shipments": 3, "annual_shipments": 1,
        "notable_brands": [], "featured": False,
    },
    # ── Electronics & Accessories ──────────────────────────────────
    {
        "name": "Lite-On Electronics Guangzhou", "country": "China", "category": "Electronics & Accessories",
        "description": "Guangzhou High-Tech Industrial Zone electronics manufacturer with 2,394 documented US shipments and an estimated $8.4M in shipping spend.",
        "products": "Electronic components, power supplies, consumer electronics",
        "us_importers": 25, "total_shipments": 2394, "annual_shipments": 399,
        "notable_brands": [], "featured": True,
    },
    {
        "name": "Dongguan Suoai Electronics", "country": "China", "category": "Electronics & Accessories",
        "description": "Huangjiang Town, Dongguan electronics manufacturer producing consumer electronics, accessories, and electrical components.",
        "products": "Consumer electronics, accessories, electrical components",
        "us_importers": 13, "total_shipments": 156, "annual_shipments": 26,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Jiangsu Guang Qian Electronics", "country": "China", "category": "Electronics & Accessories",
        "description": "Dongtai Economic Development Zone, Jiangsu manufacturer of electronic components and automotive interface electronics.",
        "products": "Electronic components, automotive electronics, interface solutions",
        "us_importers": 4, "total_shipments": 37, "annual_shipments": 6,
        "notable_brands": ["BCS Automotive Interface Solutions"], "featured": False,
    },
    {
        "name": "Hangzhou Heli Electronics", "country": "China", "category": "Electronics & Accessories",
        "description": "Yuhang District, Hangzhou electronics manufacturer producing decorative and consumer electronics products for US gift and home goods importers.",
        "products": "Decorative electronics, consumer gadgets, gift electronics",
        "us_importers": 3, "total_shipments": 10, "annual_shipments": 2,
        "notable_brands": ["Demdaco"], "featured": False,
    },
    {
        "name": "Fuzhou Shontek Electronics", "country": "China", "category": "Electronics & Accessories",
        "description": "Fuzhou, Fujian electronics manufacturer specializing in consumer electronics accessories and components.",
        "products": "Electronics accessories, consumer components",
        "us_importers": 4, "total_shipments": 21, "annual_shipments": 4,
        "notable_brands": ["Innovation Specialties"], "featured": False,
    },
    {
        "name": "Hunan Frecom Electronics", "country": "China", "category": "Electronics & Accessories",
        "description": "Suxian District, Hunan electronics manufacturer producing electronic devices and accessories.",
        "products": "Electronic devices, accessories, consumer electronics",
        "us_importers": 3, "total_shipments": 28, "annual_shipments": 5,
        "notable_brands": [], "featured": False,
    },
    # ── Pet Supplies ───────────────────────────────────────────────
    {
        "name": "Shenzhen Aiyang Pet Products", "country": "China", "category": "Pet Supplies",
        "description": "Longcheng, Shenzhen pet products manufacturer with 379 US-bound shipments on record, producing pet accessories, toys, and supplies.",
        "products": "Pet toys, accessories, collars, beds, grooming supplies",
        "us_importers": 8, "total_shipments": 379, "annual_shipments": 63,
        "notable_brands": ["Tamir Group", "Dmax Technology"], "featured": True,
    },
    {
        "name": "Charmway Industries", "country": "Vietnam", "category": "Pet Supplies",
        "description": "Hai Duong Province, Vietnam manufacturer producing pest control products and household pest management solutions for major US brands.",
        "products": "Pest traps, pest control products, household management solutions",
        "us_importers": 5, "total_shipments": 35, "annual_shipments": 6,
        "notable_brands": ["Woodstream"], "featured": False,
    },
    {
        "name": "Dong Nam (Pet/Outdoor)", "country": "Vietnam", "category": "Pet Supplies",
        "description": "Binh Duong Province, Vietnam manufacturer producing pet accessories and outdoor lifestyle products alongside activewear.",
        "products": "Pet accessories, outdoor pet gear",
        "us_importers": 5, "total_shipments": 220, "annual_shipments": 37,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Petengreat", "country": "China", "category": "Pet Supplies",
        "description": "Shenzhen-based pet supplies manufacturer producing pet accessories, toys, and care products for US wholesale distributors.",
        "products": "Pet accessories, toys, care products, feeding supplies",
        "us_importers": 4, "total_shipments": 47, "annual_shipments": 8,
        "notable_brands": ["International Pet Supplies & Distribution"], "featured": False,
    },
    {
        "name": "Shanghai Yixiao Pet Products", "country": "China", "category": "Pet Supplies",
        "description": "Songjiang District, Shanghai pet products company producing small animal accessories, cat and dog supplies, and pet care items.",
        "products": "Cat accessories, dog supplies, small animal products, pet care",
        "us_importers": 3, "total_shipments": 25, "annual_shipments": 4,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Ninghai County Dougesi Pet", "country": "China", "category": "Pet Supplies",
        "description": "Ningbo, Zhejiang pet products factory producing specialty pet accessories and supplies for smaller US pet product importers.",
        "products": "Specialty pet accessories, niche pet products",
        "us_importers": 2, "total_shipments": 8, "annual_shipments": 1,
        "notable_brands": ["Arosa Trade"], "featured": False,
    },
    # ── Food & Beverage ────────────────────────────────────────────
    {
        "name": "King Win Food & Beverage", "country": "Taiwan", "category": "Food & Beverage",
        "description": "Taiwanese food and beverage manufacturer producing jasmine green tea, oolong, matcha, lychee syrup, and passion fruit syrup for US boba tea importers.",
        "products": "Tea concentrates, fruit syrups, boba tea ingredients, matcha",
        "us_importers": 6, "total_shipments": 95, "annual_shipments": 16,
        "notable_brands": [], "featured": True,
    },
    {
        "name": "Taishan Wuhu Food Manufacturer", "country": "China", "category": "Food & Beverage",
        "description": "Taishan City, Guangdong food manufacturer producing packaged and preserved food products for US Asian food importers.",
        "products": "Packaged foods, preserved items, Asian food products",
        "us_importers": 4, "total_shipments": 48, "annual_shipments": 8,
        "notable_brands": ["Super World Trade"], "featured": False,
    },
    {
        "name": "Saigon Spices Import & Export", "country": "Vietnam", "category": "Food & Beverage",
        "description": "Ho Chi Minh City spice exporter specializing in Vietnamese black pepper, spices, and dried herbs for US food importers.",
        "products": "Black pepper, spices, dried herbs, Vietnamese agricultural products",
        "us_importers": 2, "total_shipments": 3, "annual_shipments": 1,
        "notable_brands": ["Unistel Industries"], "featured": False,
    },
    {
        "name": "Vinaxo", "country": "Vietnam", "category": "Food & Beverage",
        "description": "Dong Thap Province, Vietnam agricultural food products exporter focusing on nuts, dried fruits, and snacks for US specialty food markets.",
        "products": "Nuts, dried fruits, snacks, agricultural products",
        "us_importers": 3, "total_shipments": 11, "annual_shipments": 2,
        "notable_brands": ["Mixed Nuts"], "featured": False,
    },
    {
        "name": "Vinnature", "country": "Vietnam", "category": "Food & Beverage",
        "description": "Hoa Binh Province, Vietnam natural food and agricultural products exporter supplying US health food and specialty food importers.",
        "products": "Natural foods, agricultural products, health food ingredients",
        "us_importers": 3, "total_shipments": 11, "annual_shipments": 2,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Shandong Deliwin Food", "country": "China", "category": "Food & Beverage",
        "description": "Tengzhou City, Shandong food manufacturer producing processed and packaged food products for US food service and retail importers.",
        "products": "Processed foods, packaged goods, food service products",
        "us_importers": 3, "total_shipments": 13, "annual_shipments": 2,
        "notable_brands": ["Colorado Boxed Beef"], "featured": False,
    },
    {
        "name": "Gia Phuoc Import & Export", "country": "Vietnam", "category": "Food & Beverage",
        "description": "Hai Phong City, Vietnam food import-export company specializing in Vietnamese agricultural products and processed foods.",
        "products": "Agricultural products, processed foods, Vietnamese exports",
        "us_importers": 2, "total_shipments": 23, "annual_shipments": 4,
        "notable_brands": ["Goldman Import"], "featured": False,
    },
    # ── Toys & Games ───────────────────────────────────────────────
    {
        "name": "Zhongshan Yong Sheng Toys Factory", "country": "China", "category": "Toys & Games",
        "description": "Zhongshan, Guangdong toy manufacturer producing action figures and branded toys for Hasbro, with an estimated export value of $12.78M.",
        "products": "Action figures, plastic toys, licensed toys, character merchandise",
        "us_importers": 5, "total_shipments": 233, "annual_shipments": 39,
        "notable_brands": ["Hasbro"], "featured": True,
    },
    {
        "name": "Taicang DB Toys Manufacturing", "country": "China", "category": "Toys & Games",
        "description": "Fuqiao Town, Taicang toy manufacturer producing audio toys, plush animals, and character merchandise. Primary supplier for Tonies, the popular audio toy platform.",
        "products": "Audio toys, plush toys, figurines, character merchandise",
        "us_importers": 8, "total_shipments": 351, "annual_shipments": 59,
        "notable_brands": ["Tonies US"], "featured": True,
    },
    {
        "name": "Digo Toys Industrial", "country": "China", "category": "Toys & Games",
        "description": "Chenghai District, Shantou toy manufacturer — Chenghai being China's 'toy capital' — with 634 documented US-bound shipments.",
        "products": "Plastic toys, novelty items, promotional toys, wholesale toys",
        "us_importers": 10, "total_shipments": 634, "annual_shipments": 106,
        "notable_brands": ["VM International"], "featured": True,
    },
    {
        "name": "Yiwu Xiangtiange Educational Toys", "country": "China", "category": "Toys & Games",
        "description": "Yiwu Economic-Technological Development Area toy manufacturer specializing in wooden educational toys and learning games.",
        "products": "Wooden educational toys, learning games, STEM toys, development toys",
        "us_importers": 6, "total_shipments": 85, "annual_shipments": 14,
        "notable_brands": [], "featured": False,
    },
    {
        "name": "Shenzhen Qinghong Toys", "country": "China", "category": "Toys & Games",
        "description": "Longgang District, Shenzhen toy manufacturer producing electronic toys, novelty items, and consumer goods for US niche brands.",
        "products": "Electronic toys, novelty items, light-up toys",
        "us_importers": 3, "total_shipments": 4, "annual_shipments": 1,
        "notable_brands": ["Lumieworld.com"], "featured": False,
    },
    {
        "name": "Yiwu Binli Toys Factory", "country": "China", "category": "Toys & Games",
        "description": "Shangxi Town, Yiwu City toy factory producing novelty toys, party items, and small plastic toys for US wholesale buyers.",
        "products": "Novelty toys, party items, plastic toys, wholesale goods",
        "us_importers": 3, "total_shipments": 6, "annual_shipments": 1,
        "notable_brands": ["RGA Wonder Products"], "featured": False,
    },
    {
        "name": "Shantou Chengji Toys and Gifts", "country": "China", "category": "Toys & Games",
        "description": "Chenghai District, Shantou toy and gift manufacturer producing novelty toys, promotional items, and gifting products for US wholesale buyers.",
        "products": "Novelty toys, promotional gifts, seasonal toys",
        "us_importers": 2, "total_shipments": 3, "annual_shipments": 1,
        "notable_brands": [], "featured": False,
    },
]

SHOPIFY_STORES = [
    # ── Apparel & Fashion ──────────────────────────────────────────
    {"name": "Wild Oak Boutique", "slug": "wild-oak-boutique", "url": "https://wildoakboutique.com", "category": "apparel", "description": "Women's clothing boutique based in Sioux Falls, SD. INC 5000 fastest-growing company in South Dakota, running a 6,000+ sq ft warehouse on Shopify.", "founded_year": 2016, "employee_count": "10–30", "revenue_tier": "growing", "annual_revenue_est": "$3M–$6M", "sku_count": "400–600", "supplier_count": "8–12", "traffic_tier": "medium", "location": "Sioux Falls, SD", "shopify_plus": False, "featured": True, "notable_for": "INC 5000 fastest-growing in South Dakota. Classic boutique that outgrew manual inventory tracking."},
    {"name": "Morning Lavender", "slug": "morning-lavender", "url": "https://morninglavender.com", "category": "apparel", "description": "Women's fashion boutique in Los Angeles focused on feminine, floral styles with a strong Instagram following.", "founded_year": 2014, "employee_count": "25–50", "revenue_tier": "growing", "annual_revenue_est": "$2M–$4M", "sku_count": "200–400", "supplier_count": "6–10", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": False, "featured": True, "notable_for": "~28 employees managing seasonal collections across multiple suppliers. Social-first DTC model."},
    {"name": "Set Active", "slug": "set-active", "url": "https://setactive.co", "category": "apparel", "description": "LA-based activewear brand known for matching set collections in trend-forward colorways. Drop-based business model.", "founded_year": 2019, "employee_count": "10–30", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "80–150", "supplier_count": "3–5", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": False, "featured": True, "notable_for": "Sources from Yotex Apparel Shanghai. Drops sell out in hours — requires precise supplier coordination."},
    {"name": "Civil Clothing", "slug": "civil-clothing", "url": "https://civilclothing.com", "category": "apparel", "description": "Independent streetwear and lifestyle brand with quality basics, graphic tees, and limited-run drops.", "founded_year": 2010, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "50–120", "supplier_count": "3–6", "traffic_tier": "small", "location": "United States", "shopify_plus": False, "featured": False, "notable_for": "Sources from Nantong Fortune Fashion. Typical independent brand managing drops across a small SKU catalog."},
    {"name": "Pact Apparel", "slug": "pact-apparel", "url": "https://wearpact.com", "category": "apparel", "description": "Organic cotton basics brand with B Corp certification focused on affordable, sustainable everyday essentials.", "founded_year": 2009, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$15M–$25M", "sku_count": "200–350", "supplier_count": "8–15", "traffic_tier": "medium", "location": "Boulder, CO", "shopify_plus": False, "featured": False, "notable_for": "Managing 200+ organic cotton SKUs with zero overproduction tolerance. Sustainable apparel = tight inventory discipline."},
    {"name": "Faherty Brand", "slug": "faherty-brand", "url": "https://fahertybrand.com", "category": "apparel", "description": "Premium coastal lifestyle apparel with DTC roots and 40+ retail stores.", "founded_year": 2013, "employee_count": "200–500", "revenue_tier": "scaleup", "annual_revenue_est": "$40M–$60M", "sku_count": "300–500", "supplier_count": "10–20", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": True, "featured": False, "notable_for": "Sources from Vicmark Fashions Cambodia. Raised $66M. Omnichannel inventory across DTC + 40+ retail stores."},
    {"name": "Taylor Stitch", "slug": "taylor-stitch", "url": "https://taylorstitch.com", "category": "apparel", "description": "San Francisco menswear brand known for workshop-model pre-orders and premium durable clothing.", "founded_year": 2010, "employee_count": "30–60", "revenue_tier": "growing", "annual_revenue_est": "$8M–$15M", "sku_count": "100–200", "supplier_count": "8–12", "traffic_tier": "medium", "location": "San Francisco, CA", "shopify_plus": False, "featured": False, "notable_for": "Pre-order model reduces inventory risk but requires precise supplier timeline management."},
    {"name": "Pistol Lake", "slug": "pistol-lake", "url": "https://pistollake.com", "category": "apparel", "description": "Minimalist menswear brand making everyday basics from sustainable fabrics. DTC-only, small team.", "founded_year": 2013, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "30–60", "supplier_count": "2–4", "traffic_tier": "small", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "Ultra-lean team managing a focused SKU catalog. Every stock-out directly impacts subscription retention."},
    {"name": "Wool&", "slug": "wool-and", "url": "https://woolandclothing.com", "category": "apparel", "description": "Women's merino wool clothing brand with a 100-day wear challenge. Focused on quality over quantity.", "founded_year": 2018, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "40–80", "supplier_count": "3–6", "traffic_tier": "small", "location": "Seattle, WA", "shopify_plus": False, "featured": False, "notable_for": "Single-material strategy with few suppliers but high per-unit cost — stock-outs are expensive."},
    {"name": "Chubbies", "slug": "chubbies", "url": "https://chubbiesshorts.com", "category": "apparel", "description": "Men's shorts and casual lifestyle brand known for retro-inspired designs and irreverent marketing.", "founded_year": 2011, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$20M–$35M", "sku_count": "150–250", "supplier_count": "8–15", "traffic_tier": "medium", "location": "Austin, TX", "shopify_plus": True, "featured": False, "notable_for": "Seasonal inventory spike in summer requires 6+ month advance supplier planning. Acquired by Solo Brands 2021."},
    {"name": "Entireworld", "slug": "entireworld", "url": "https://theentireworld.com", "category": "apparel", "description": "New York basics brand known for colorful, oversized sweatshirts. DTC-only, low SKU count, high repeat purchase.", "founded_year": 2018, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "20–50", "supplier_count": "2–4", "traffic_tier": "small", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Proves that fewer SKUs with deeper inventory per color/size can outperform larger catalogs. Tight supplier relationships essential."},
    {"name": "Sendero Provisions", "slug": "sendero-provisions", "url": "https://senderoprovisions.com", "category": "apparel", "description": "Austin-based outdoor and workwear brand with Texas roots. Apparel and accessories built for the outdoors.", "founded_year": 2016, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$2M–$4M", "sku_count": "80–150", "supplier_count": "4–8", "traffic_tier": "small", "location": "Austin, TX", "shopify_plus": False, "featured": False, "notable_for": "Seasonal outdoor business — spring/fall launches require disciplined supplier reorder cycles."},
    # ── Home & Garden ──────────────────────────────────────────────
    {"name": "George and Willy", "slug": "george-and-willy", "url": "https://georgeandwilly.com", "category": "home", "description": "New Zealand-founded workspace and retail display products brand. Chalk menu boards, display rails, and retail fixture systems.", "founded_year": 2014, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$2M–$4M", "sku_count": "60–100", "supplier_count": "4–7", "traffic_tier": "small", "location": "Tauranga, New Zealand", "shopify_plus": False, "featured": True, "notable_for": "Ships to 80+ countries. Left Inventory Planner over GMV pricing. Small team, global reach, real inventory complexity."},
    {"name": "Keap Candles", "slug": "keap-candles", "url": "https://keapcandles.com", "category": "home", "description": "Subscription candle brand using natural ingredients. Ships seasonal scents direct to subscribers monthly.", "founded_year": 2017, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "20–40", "supplier_count": "3–6", "traffic_tier": "small", "location": "Brooklyn, NY", "shopify_plus": False, "featured": True, "notable_for": "Subscription model requires demand forecasting months ahead to coordinate with candle suppliers. Perfect automated reorder use case."},
    {"name": "Brightland", "slug": "brightland", "url": "https://brightland.co", "category": "home", "description": "Premium California olive oil and vinegar brand sourced from single farms. DTC-first with growing wholesale.", "founded_year": 2018, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "15–25", "supplier_count": "4–8", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": False, "featured": True, "notable_for": "Farm sourcing + overseas packaging suppliers = dual supply chain. Growing from 1 to 20 SKUs while keeping suppliers aligned."},
    {"name": "Made In Cookware", "slug": "made-in-cookware", "url": "https://madeincookware.com", "category": "home", "description": "Professional-grade DTC cookware made with heritage manufacturers in France, Italy, and the US.", "founded_year": 2017, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$40M–$60M", "sku_count": "80–150", "supplier_count": "8–15", "traffic_tier": "large", "location": "Austin, TX", "shopify_plus": True, "featured": False, "notable_for": "Managing multi-country manufacturing relationships on one Shopify store. Long lead times from European factories require advance PO planning."},
    {"name": "Letterfolk", "slug": "letterfolk", "url": "https://letterfolk.com", "category": "home", "description": "Design-forward letter boards, felt boards, and graphic art. Cult following among home decorators and gift givers.", "founded_year": 2015, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "50–100", "supplier_count": "3–6", "traffic_tier": "small", "location": "Salt Lake City, UT", "shopify_plus": False, "featured": False, "notable_for": "Seasonal spike at holidays requires early reorder planning. Simple product line but complex supplier coordination at peak."},
    {"name": "Areaware", "slug": "areaware", "url": "https://areaware.com", "category": "home", "description": "Brooklyn design studio making playful, thoughtful objects for the home. Objects, games, and accessories.", "founded_year": 2008, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$3M–$6M", "sku_count": "100–200", "supplier_count": "8–15", "traffic_tier": "small", "location": "Brooklyn, NY", "shopify_plus": False, "featured": False, "notable_for": "Wide SKU range across design objects + games. Multiple manufacturing partners in Asia and Europe require concurrent PO management."},
    {"name": "The Citizenry", "slug": "the-citizenry", "url": "https://the-citizenry.com", "category": "home", "description": "Premium artisan home goods sourced from craftspeople worldwide. Rugs, bedding, furniture, and decor.", "founded_year": 2014, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$10M–$20M", "sku_count": "150–250", "supplier_count": "30–50", "traffic_tier": "medium", "location": "Dallas, TX", "shopify_plus": True, "featured": False, "notable_for": "50+ artisan suppliers across 20+ countries. The complexity of managing this many overseas supplier relationships manually is exactly what Reorderly solves."},
    {"name": "Jungalow", "slug": "jungalow", "url": "https://jungalow.com", "category": "home", "description": "Bohemian home decor brand by designer Justina Blakeney. Textiles, artwork, plants, and colorful home accessories.", "founded_year": 2009, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "200–400", "supplier_count": "10–20", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "Large SKU count across imported textiles and decor. Multiple overseas suppliers with varying lead times."},
    {"name": "East Fork Pottery", "slug": "east-fork-pottery", "url": "https://eastfork.com", "category": "home", "description": "Asheville-based ceramics brand making everyday pottery in the US. Plates, mugs, bowls, and vessels.", "founded_year": 2009, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$8M–$15M", "sku_count": "40–80", "supplier_count": "5–10", "traffic_tier": "medium", "location": "Asheville, NC", "shopify_plus": False, "featured": False, "notable_for": "US manufacturing means supplier bottlenecks are domestic but still require coordinated reorder systems across clay, glaze, and packaging suppliers."},
    # ── Beauty & Personal Care ─────────────────────────────────────
    {"name": "Jones Road Beauty", "slug": "jones-road-beauty", "url": "https://jonesroadbeauty.com", "category": "beauty", "description": "Clean makeup brand by Bobbi Brown. No-nonsense skin-enhancing products bootstrapped to $30M+ in 3 years.", "founded_year": 2020, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$30M–$50M", "sku_count": "40–80", "supplier_count": "5–10", "traffic_tier": "medium", "location": "Montclair, NJ", "shopify_plus": False, "featured": True, "notable_for": "Bootstrapped to $30M+ in 3 years. Rapid SKU expansion requires tight supplier forecasting."},
    {"name": "Pomp & Co.", "slug": "pomp-co", "url": "https://pomp.ie", "category": "beauty", "description": "Dublin men's grooming brand with 70+ years of heritage. Premium shaving, haircare, and skincare.", "founded_year": 1951, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$500K–$2M", "sku_count": "80–150", "supplier_count": "6–10", "traffic_tier": "small", "location": "Dublin, Ireland", "shopify_plus": False, "featured": True, "notable_for": "8-year Shopify merchant with multi-supplier catalog. Heritage brand managing international supply chain manually."},
    {"name": "Kara Beauty", "slug": "kara-beauty", "url": "https://karabeauty.com", "category": "beauty", "description": "Affordable color cosmetics known for eyeshadow palettes and trend-forward makeup.", "founded_year": 2020, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "60–120", "supplier_count": "3–6", "traffic_tier": "medium", "location": "United States", "shopify_plus": False, "featured": False, "notable_for": "Sources from Pingdu Heart Girl Eyelash Factory. Fast inventory turns — beauty trends shift quarterly."},
    {"name": "Crown Affair", "slug": "crown-affair", "url": "https://crownaffair.com", "category": "beauty", "description": "Premium hair care brand focused on the ritual of caring for your hair. Oils, combs, towels, and treatments.", "founded_year": 2020, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "20–40", "supplier_count": "4–8", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Multi-material product line (haircare formulas + accessories) requires coordinating 2 separate supplier types simultaneously."},
    {"name": "Doe Lashes", "slug": "doe-lashes", "url": "https://doelashes.com", "category": "beauty", "description": "Vegan false lash brand known for natural-looking, reusable lashes. Strong Gen Z following.", "founded_year": 2019, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "30–60", "supplier_count": "2–4", "traffic_tier": "small", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "High SKU turnover — launches new lash styles each season. Tight supplier lead times critical for on-time drops."},
    {"name": "MERIT Beauty", "slug": "merit-beauty", "url": "https://meritbeauty.com", "category": "beauty", "description": "Minimalist clean beauty brand focused on multi-use, everyday essentials. No-makeup makeup aesthetic.", "founded_year": 2021, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$20M–$40M", "sku_count": "25–50", "supplier_count": "4–8", "traffic_tier": "large", "location": "New York, NY", "shopify_plus": True, "featured": False, "notable_for": "Rapid growth from 0 to $40M+ in 2 years. Scaling a cosmetics line requires precise supplier capacity planning."},
    {"name": "Saie Beauty", "slug": "saie-beauty", "url": "https://saiebeauty.com", "category": "beauty", "description": "Clean beauty brand with a focus on glowy, effortless makeup. Sustainably-packaged formulas.", "founded_year": 2019, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$10M–$20M", "sku_count": "30–60", "supplier_count": "4–8", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Clean formulation + sustainable packaging = 2 supplier tracks to coordinate. Seasonal launches require advance inventory planning."},
    {"name": "Versed Skincare", "slug": "versed-skincare", "url": "https://versed.com", "category": "beauty", "description": "Affordable clean skincare brand sold at DTC and Target. Formula-focused, no-fluff positioning.", "founded_year": 2019, "employee_count": "20–40", "revenue_tier": "scaleup", "annual_revenue_est": "$15M–$30M", "sku_count": "30–60", "supplier_count": "4–8", "traffic_tier": "large", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "DTC + retail channel requires managing two separate inventory streams from the same suppliers."},
    # ── Sports & Outdoors ──────────────────────────────────────────
    {"name": "303 Boards", "slug": "303-boards", "url": "https://303boards.com", "category": "sports", "description": "Denver skateboard and action sports retailer with 3 Colorado locations and an online store.", "founded_year": 2003, "employee_count": "5–20", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "500–1,000", "supplier_count": "20–40", "traffic_tier": "small", "location": "Denver, CO", "shopify_plus": False, "featured": True, "notable_for": "3 locations + online. Hundreds of hardgoods SKUs across boards, trucks, wheels, apparel — from 30+ brands."},
    {"name": "Whittaker Mountaineering", "slug": "whittaker-mountaineering", "url": "https://whittakermountaineering.com", "category": "sports", "description": "Iconic outdoor gear retailer near Mt. Rainier. Founded by the first American to summit Everest, now third-generation.", "founded_year": 1956, "employee_count": "20–50", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "600–1,200", "supplier_count": "30–60", "traffic_tier": "small", "location": "Ashford, WA", "shopify_plus": False, "featured": True, "notable_for": "Complex technical gear catalog, deep supplier roster, strong seasonality. Manual PO emails were a real operational bottleneck."},
    {"name": "Grand Trunk", "slug": "grand-trunk", "url": "https://grandtrunk.com", "category": "sports", "description": "Hammock and outdoor lifestyle brand. Popularized camping hammocks in the US.", "founded_year": 2001, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$3M–$6M", "sku_count": "50–100", "supplier_count": "4–8", "traffic_tier": "small", "location": "United States", "shopify_plus": False, "featured": False, "notable_for": "Sources from Qingdao Wintrak. Outdoor season = 90-day advance planning with overseas suppliers."},
    {"name": "Cotopaxi", "slug": "cotopaxi", "url": "https://cotopaxi.com", "category": "sports", "description": "Mission-driven outdoor gear brand donating 1% of revenue to fighting poverty. Known for colorful Del Dia bags.", "founded_year": 2014, "employee_count": "200–500", "revenue_tier": "scaleup", "annual_revenue_est": "$50M–$80M", "sku_count": "200–400", "supplier_count": "15–25", "traffic_tier": "medium", "location": "Salt Lake City, UT", "shopify_plus": True, "featured": False, "notable_for": "B Corp. Raised $73M. One-of-a-kind Del Dia products make standard inventory management impossible — requires custom workflows."},
    {"name": "Janji", "slug": "janji", "url": "https://janjisports.com", "category": "sports", "description": "Running apparel brand donating a portion of sales to global water access. Technical run gear with a mission.", "founded_year": 2012, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "60–120", "supplier_count": "4–8", "traffic_tier": "small", "location": "Boston, MA", "shopify_plus": False, "featured": False, "notable_for": "Seasonal run gear drops with overseas manufacturing. Coordinating production and POs around race season calendar."},
    {"name": "District Vision", "slug": "district-vision", "url": "https://districtvision.com", "category": "sports", "description": "Mindful running and sports brand combining performance apparel with meditation and wellness.", "founded_year": 2016, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "30–60", "supplier_count": "3–6", "traffic_tier": "small", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Small team, premium price point, long lead times from technical fabric suppliers. Every stock-out is revenue lost."},
    {"name": "Ten Thousand", "slug": "ten-thousand", "url": "https://tenthousand.cc", "category": "sports", "description": "Men's training apparel brand focused on durable, functional design for serious athletes.", "founded_year": 2017, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "40–80", "supplier_count": "4–8", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Performance apparel with tight production runs. Raised $8M. Balancing core replenishment SKUs vs. seasonal launches requires dual reorder logic."},
    {"name": "Oru Kayak", "slug": "oru-kayak", "url": "https://orukayak.com", "category": "sports", "description": "Origami-inspired folding kayaks that pack into a backpack. DTC and outdoor retailer distribution.", "founded_year": 2012, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "10–20", "supplier_count": "3–6", "traffic_tier": "small", "location": "Oakland, CA", "shopify_plus": False, "featured": False, "notable_for": "Very few SKUs, very high unit cost. One production delay from overseas can wipe out an entire season's revenue."},
    # ── Pet Supplies ───────────────────────────────────────────────
    {"name": "Wild One", "slug": "wild-one", "url": "https://wildone.com", "category": "pets", "description": "Premium pet accessories with clean, modern design. Collars, leashes, beds, and toys for design-forward pet owners.", "founded_year": 2018, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$3M–$6M", "sku_count": "50–100", "supplier_count": "4–8", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": True, "notable_for": "Stock-outs hurt brand loyalty. Small team managing accessories across 4–8 overseas manufacturers."},
    {"name": "Modkat", "slug": "modkat", "url": "https://modkat.com", "category": "pets", "description": "Award-winning minimalist cat litter box brand. Brooklyn-founded, DTC-first, design-led.", "founded_year": 2010, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$2M–$4M", "sku_count": "15–25", "supplier_count": "2–4", "traffic_tier": "small", "location": "Brooklyn, NY", "shopify_plus": False, "featured": True, "notable_for": "Left Inventory Planner when price tripled. Small team, single-niche catalog, China manufacturing with 90-day lead times."},
    {"name": "Harry Barker", "slug": "harry-barker", "url": "https://harrybarker.com", "category": "pets", "description": "Eco-friendly pet products brand using organic and recycled materials. Beds, collars, toys, accessories.", "founded_year": 2003, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "100–200", "supplier_count": "8–15", "traffic_tier": "small", "location": "Charleston, SC", "shopify_plus": False, "featured": False, "notable_for": "100+ sustainable pet SKUs across 10+ eco-certified manufacturers. Managing compliance + inventory simultaneously."},
    {"name": "P.L.A.Y. Pet Lifestyles", "slug": "play-pet-lifestyles", "url": "https://petplay.com", "category": "pets", "description": "Premium pet lifestyle brand making plush toys, beds, and accessories with eco-friendly materials.", "founded_year": 2009, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "80–150", "supplier_count": "5–10", "traffic_tier": "small", "location": "San Francisco, CA", "shopify_plus": False, "featured": False, "notable_for": "Seasonal holiday toy catalog requires 6-month advance planning. Managing plush SKUs from Asia with long production cycles."},
    {"name": "Zee.Dog", "slug": "zee-dog", "url": "https://zee-dog.com", "category": "pets", "description": "Brazilian pet accessories brand known for colorful, design-forward collars, leashes, and harnesses.", "founded_year": 2012, "employee_count": "30–60", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "100–200", "supplier_count": "6–12", "traffic_tier": "medium", "location": "São Paulo, Brazil", "shopify_plus": False, "featured": False, "notable_for": "International DTC brand shipping to US from Brazil-based suppliers. Complex cross-border supplier management."},
    {"name": "Wild Earth", "slug": "wild-earth", "url": "https://wildearth.com", "category": "pets", "description": "Plant-based dog food brand using koji protein. Sustainable alternative to meat-based pet food.", "founded_year": 2019, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "10–20", "supplier_count": "3–6", "traffic_tier": "small", "location": "Berkeley, CA", "shopify_plus": False, "featured": False, "notable_for": "Consumable product with subscription demand. Tight production forecasting required — running out of food = immediate churn."},
    {"name": "Sundays For Dogs", "slug": "sundays-for-dogs", "url": "https://sundaysfordogs.com", "category": "pets", "description": "Air-dried dog food brand made from whole ingredients. Subscription-first DTC model.", "founded_year": 2019, "employee_count": "20–40", "revenue_tier": "growing", "annual_revenue_est": "$5M–$12M", "sku_count": "5–15", "supplier_count": "4–8", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Subscription pet food: out-of-stock = subscriber churn. Supplier forecasting directly tied to subscription cohort growth."},
    # ── Food & Beverage ────────────────────────────────────────────
    {"name": "Brightland (Food)", "slug": "brightland-food", "url": "https://brightland.co", "category": "food", "description": "Premium California olive oil and vinegar direct-to-consumer. Farm-sourced, single-origin.", "founded_year": 2018, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "15–25", "supplier_count": "4–8", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": False, "featured": True, "notable_for": "Farm + packaging supplier coordination. Seasonal harvest windows require advance PO timing."},
    {"name": "Chomps", "slug": "chomps", "url": "https://chomps.com", "category": "food", "description": "Clean-ingredient meat stick brand bootstrapped to $50M+ before Mondelēz acquisition for reported $900M.", "founded_year": 2012, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$50M+", "sku_count": "15–30", "supplier_count": "3–6", "traffic_tier": "medium", "location": "Chicago, IL", "shopify_plus": True, "featured": False, "notable_for": "High-velocity consumable. Before acquisition: out-of-stocks directly throttled growth. Classic inventory-first DTC food brand."},
    {"name": "Chamberlain Coffee", "slug": "chamberlain-coffee", "url": "https://chamberlaincoffee.com", "category": "food", "description": "Specialty coffee and matcha brand by YouTuber Emma Chamberlain. Strong Gen Z audience.", "founded_year": 2019, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$5M–$12M", "sku_count": "20–40", "supplier_count": "4–8", "traffic_tier": "large", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "Creator brand with rapid SKU growth. Small ops team managing coffee, matcha, and accessories from multiple suppliers."},
    {"name": "Fly By Jing", "slug": "fly-by-jing", "url": "https://flybyjing.com", "category": "food", "description": "Sichuan-inspired chili sauces, crispy chili oils, and condiments. DTC-first, premium positioning.", "founded_year": 2018, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "10–20", "supplier_count": "3–6", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "Imported condiments from Sichuan. Production runs from China + US packaging require coordinated lead times."},
    {"name": "Graza", "slug": "graza", "url": "https://graza.co", "category": "food", "description": "Spanish single-origin olive oil in squeeze bottles. Made 'Drizzle' a cultural moment in food DTC.", "founded_year": 2022, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$10M–$20M", "sku_count": "5–10", "supplier_count": "2–4", "traffic_tier": "large", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Viral growth from 2 SKUs to $10M+ in Year 1. Single-origin supply from Spain means supplier relationships are existential."},
    {"name": "Diaspora Co.", "slug": "diaspora-co", "url": "https://diasporaco.com", "category": "food", "description": "Single-origin spice company sourcing directly from small farms across South Asia.", "founded_year": 2017, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "20–40", "supplier_count": "15–25", "traffic_tier": "small", "location": "Brooklyn, NY", "shopify_plus": False, "featured": False, "notable_for": "25+ small farm suppliers across India, Sri Lanka, Nepal. Most complex supplier management challenge relative to revenue size."},
    {"name": "Deux", "slug": "deux", "url": "https://eatdeux.com", "category": "food", "description": "Functional cookie dough brand with adaptogens and vitamins. Aimed at health-conscious snackers.", "founded_year": 2021, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "10–20", "supplier_count": "3–6", "traffic_tier": "small", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "Functional ingredient supply chain (adaptogens + food-grade) requires managing 2 types of suppliers simultaneously."},
    {"name": "Burlap & Barrel", "slug": "burlap-barrel", "url": "https://burlapandbarrel.com", "category": "food", "description": "Single-origin spices from small farms globally. Transparent supply chain, chef-favorite seasonings.", "founded_year": 2017, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "30–60", "supplier_count": "20–35", "traffic_tier": "small", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "35+ farm suppliers across 20+ countries. The supply chain IS the product — requires the tightest possible PO tracking."},
    # ── Health & Wellness ──────────────────────────────────────────
    {"name": "Beardbrand", "slug": "beardbrand", "url": "https://beardbrand.com", "category": "health", "description": "Men's grooming pioneer focused on beard care, hair care, and skincare. One of the original DTC grooming brands.", "founded_year": 2012, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$7M–$12M", "sku_count": "50–80", "supplier_count": "4–8", "traffic_tier": "medium", "location": "Austin, TX", "shopify_plus": False, "featured": True, "notable_for": "Bootstrapped to $7M+ ARR under 30 people. Built the DTC grooming playbook. Managing seasonal demand spikes manually."},
    {"name": "Hydrant", "slug": "hydrant", "url": "https://drinkhydrant.com", "category": "health", "description": "Electrolyte drink mix focused on rapid hydration. Subscription and single-serve formats.", "founded_year": 2018, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "15–30", "supplier_count": "3–6", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Subscription consumables require demand forecasting months ahead. Flavor launches add SKU complexity fast."},
    {"name": "Altenew", "slug": "altenew", "url": "https://altenew.com", "category": "health", "description": "Crafting and stationery brand — stamps, inks, dies, paper crafting. 9-year Shopify merchant, global customer base.", "founded_year": 2015, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$10M–$20M", "sku_count": "500–800", "supplier_count": "8–15", "traffic_tier": "medium", "location": "East Syracuse, NY", "shopify_plus": False, "featured": True, "notable_for": "500+ SKUs across inks, dies, stamps. Operations on 4 continents. Inventory sync reliability is business-critical."},
    {"name": "Needed", "slug": "needed", "url": "https://thisisneeded.com", "category": "health", "description": "Evidence-based prenatal supplements subscription brand for women from pre-conception through postpartum.", "founded_year": 2019, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "15–30", "supplier_count": "4–8", "traffic_tier": "medium", "location": "San Francisco, CA", "shopify_plus": False, "featured": False, "notable_for": "Subscription supplements with strict regulatory requirements. Running out of stock in this category loses customers permanently."},
    {"name": "Transparent Labs", "slug": "transparent-labs", "url": "https://transparentlabs.com", "category": "health", "description": "Science-backed sports nutrition brand with no artificial ingredients. Protein, pre-workout, vitamins.", "founded_year": 2015, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$15M–$30M", "sku_count": "60–100", "supplier_count": "5–10", "traffic_tier": "large", "location": "Salt Lake City, UT", "shopify_plus": True, "featured": False, "notable_for": "High-velocity supplement catalog. Flavors and formulations turn over fast. Ingredient suppliers + contract manufacturers = dual PO workflow."},
    {"name": "Beam", "slug": "beam", "url": "https://beamorganics.com", "category": "health", "description": "Functional wellness brand known for Dream sleep powder and hemp-based supplements.", "founded_year": 2018, "employee_count": "20–40", "revenue_tier": "growing", "annual_revenue_est": "$8M–$15M", "sku_count": "20–40", "supplier_count": "4–8", "traffic_tier": "medium", "location": "Boston, MA", "shopify_plus": False, "featured": False, "notable_for": "Dream sleep powder went viral. Demand spikes require advance ingredient procurement coordination across hemp and functional ingredient suppliers."},
    {"name": "KOS Organic", "slug": "kos-organic", "url": "https://kos.com", "category": "health", "description": "Organic plant-based protein powders and supplements. Clean label, full-spectrum ingredients.", "founded_year": 2018, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$5M–$12M", "sku_count": "20–40", "supplier_count": "6–12", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Organic certification adds supply chain complexity — certified ingredient suppliers have long lead times and limited capacity."},
    # ── Toys & Games ───────────────────────────────────────────────
    {"name": "Tonies US", "slug": "tonies-us", "url": "https://us.tonies.com", "category": "toys", "description": "Audio toy platform using character figurines to play stories and music without screens.", "founded_year": 2016, "employee_count": "50–200", "revenue_tier": "scaleup", "annual_revenue_est": "$30M–$60M", "sku_count": "500–800", "supplier_count": "3–6", "traffic_tier": "large", "location": "New York, NY", "shopify_plus": True, "featured": True, "notable_for": "Manufactures via Taicang DB Toys. 500+ character figurines each needing precise inventory coordination with a single factory."},
    {"name": "Treehouse Toys", "slug": "treehouse-toys", "url": "https://treehousetoys.us", "category": "toys", "description": "Independent toy retailer with 2 locations in NH and ME. Curates premium, educational, imaginative toys.", "founded_year": 2002, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "300–600", "supplier_count": "20–40", "traffic_tier": "small", "location": "Portsmouth, NH", "shopify_plus": False, "featured": True, "notable_for": "2 retail locations + online store, 300+ SKUs across 30+ brand suppliers. Classic independent retailer inventory challenge."},
    {"name": "Fat Brain Toys", "slug": "fat-brain-toys", "url": "https://fatbraintoys.com", "category": "toys", "description": "Independent toy company making award-winning developmental and specialty toys. DTC and wholesale.", "founded_year": 2002, "employee_count": "20–40", "revenue_tier": "scaleup", "annual_revenue_est": "$10M–$20M", "sku_count": "200–400", "supplier_count": "10–20", "traffic_tier": "medium", "location": "Omaha, NE", "shopify_plus": False, "featured": False, "notable_for": "200+ proprietary toy SKUs manufactured in Asia. Seasonal Q4 spike requires 6+ month advance supplier planning."},
    {"name": "Monti Kids", "slug": "monti-kids", "url": "https://montikids.com", "category": "toys", "description": "Subscription Montessori toy company. Age-appropriate developmental toy boxes delivered quarterly.", "founded_year": 2016, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$3M–$6M", "sku_count": "50–100", "supplier_count": "5–10", "traffic_tier": "small", "location": "San Francisco, CA", "shopify_plus": False, "featured": False, "notable_for": "Subscription toy boxes require forward forecasting of subscriber cohort demand 90+ days out to order from overseas manufacturers."},
    {"name": "Lovevery", "slug": "lovevery", "url": "https://lovevery.com", "category": "toys", "description": "Evidence-based developmental toy subscription for babies and toddlers. Stage-based play kits.", "founded_year": 2017, "employee_count": "100–200", "revenue_tier": "scaleup", "annual_revenue_est": "$100M+", "sku_count": "100–200", "supplier_count": "10–20", "traffic_tier": "large", "location": "Boise, ID", "shopify_plus": True, "featured": False, "notable_for": "Raised $100M. Subscription model with predictable demand — but getting forecasting wrong means breaking your delivery promise to parents."},

    # ── Apparel (additional) ───────────────────────────────────────────────
    {"name": "Kirrin Finch", "slug": "kirrin-finch", "url": "https://kirrinfinch.com", "category": "apparel", "description": "Gender-neutral menswear-inspired clothing for women and non-binary people. Wedding wear and officewear focus.", "founded_year": 2016, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "80–150", "supplier_count": "4–8", "traffic_tier": "small", "location": "Brooklyn, NY", "shopify_plus": False, "featured": False, "notable_for": "Small team, niche apparel brand sourcing internationally. Seasonal wedding season demand spikes require advance PO planning."},
    {"name": "Outdoor Voices", "slug": "outdoor-voices", "url": "https://outdoorvoices.com", "category": "apparel", "description": "Activewear brand positioning activity as joyful rather than performance. Technical fabrics, bright colors.", "founded_year": 2013, "employee_count": "100–200", "revenue_tier": "scaleup", "annual_revenue_est": "$30M–$50M", "sku_count": "150–300", "supplier_count": "10–20", "traffic_tier": "large", "location": "Austin, TX", "shopify_plus": True, "featured": False, "notable_for": "Raised $64M. Complex multi-color, multi-size SKU matrix with international manufacturing. Supplier coordination at scale."},
    {"name": "Gravel Travel", "slug": "gravel-travel", "url": "https://graveltravelbrand.com", "category": "apparel", "description": "Travel-focused menswear brand making wrinkle-free, odor-resistant performance shirts for frequent flyers.", "founded_year": 2019, "employee_count": "5–10", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "30–60", "supplier_count": "3–6", "traffic_tier": "small", "location": "United States", "shopify_plus": False, "featured": False, "notable_for": "Small team, performance fabric sourcing from Asia. Long lead times on technical textiles require forward purchase orders."},
    {"name": "Hackwith Design House", "slug": "hackwith-design-house", "url": "https://hackwithdesignhouse.com", "category": "apparel", "description": "Women's minimalist fashion brand made in Minneapolis. Small-batch, ethical US manufacturing.", "founded_year": 2013, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "100–200", "supplier_count": "5–10", "traffic_tier": "small", "location": "Minneapolis, MN", "shopify_plus": False, "featured": False, "notable_for": "US manufacturing with a rotating seasonal catalog. Managing fabric and trim suppliers domestically while keeping costs competitive."},
    {"name": "Wellen", "slug": "wellen", "url": "https://wellensurf.com", "category": "apparel", "description": "Sustainable surf and coastal apparel made from recycled materials. Wetsuit-to-shirt lifestyle brand.", "founded_year": 2009, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "80–150", "supplier_count": "5–10", "traffic_tier": "small", "location": "Santa Barbara, CA", "shopify_plus": False, "featured": False, "notable_for": "Recycled material sourcing adds supplier complexity. Surf seasonality = hard-to-predict demand windows requiring advance ordering."},
    {"name": "Tradlands", "slug": "tradlands", "url": "https://tradlands.com", "category": "apparel", "description": "Women's classic-cut shirts and workwear inspired by menswear. Made in ethical overseas factories.", "founded_year": 2014, "employee_count": "5–10", "revenue_tier": "growing", "annual_revenue_est": "$1M–$2M", "sku_count": "40–80", "supplier_count": "3–6", "traffic_tier": "small", "location": "Buffalo, NY", "shopify_plus": False, "featured": False, "notable_for": "Small-batch overseas production with seasonal launches. Small team managing international supplier relationships manually."},
    {"name": "Buck Mason", "slug": "buck-mason", "url": "https://buckmason.com", "category": "apparel", "description": "American menswear brand focused on classic, well-made basics. T-shirts, denim, and outerwear.", "founded_year": 2013, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$20M–$40M", "sku_count": "100–200", "supplier_count": "8–15", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": True, "featured": False, "notable_for": "DTC + 3 retail stores. Core basics require tight replenishment cycles to avoid out-of-stocks on top-selling SKUs year-round."},
    {"name": "Copper + Crane", "slug": "copper-crane", "url": "https://copperandcrane.com", "category": "apparel", "description": "Western-inspired women's clothing and accessories boutique. Hats, boots, fringe, and ranch style.", "founded_year": 2018, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$500K–$2M", "sku_count": "200–400", "supplier_count": "10–20", "traffic_tier": "small", "location": "Texas", "shopify_plus": False, "featured": False, "notable_for": "Fast-fashion boutique model with wide SKU catalog. Trend-driven restocking requires quick PO turnaround from multiple vendors."},

    # ── Home (additional) ──────────────────────────────────────────────────
    {"name": "Lulu and Georgia", "slug": "lulu-and-georgia", "url": "https://luluandgeorgia.com", "category": "home", "description": "Curated home decor and furniture with a Southern California aesthetic. Rugs, lighting, and furniture.", "founded_year": 2012, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$20M–$40M", "sku_count": "2,000–4,000", "supplier_count": "50–100", "traffic_tier": "large", "location": "Los Angeles, CA", "shopify_plus": True, "featured": False, "notable_for": "Thousands of home decor SKUs from 50+ overseas suppliers. Managing this catalog on a Shopify store without automation is nearly impossible."},
    {"name": "Schoolhouse", "slug": "schoolhouse", "url": "https://schoolhouse.com", "category": "home", "description": "Design-forward lighting and home goods brand. Handcrafted lighting made in the US.", "founded_year": 2003, "employee_count": "100–200", "revenue_tier": "scaleup", "annual_revenue_est": "$15M–$30M", "sku_count": "500–1,000", "supplier_count": "20–40", "traffic_tier": "medium", "location": "Portland, OR", "shopify_plus": True, "featured": False, "notable_for": "500+ lighting SKUs, US and international components. Managing component-level reordering for made-to-order products."},
    {"name": "Birdies", "slug": "birdies", "url": "https://birdiesshoes.com", "category": "home", "description": "Women's flats and shoes known for comfort and style. DTC-first footwear with strong repeat purchase.", "founded_year": 2015, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "80–150", "supplier_count": "4–8", "traffic_tier": "medium", "location": "San Francisco, CA", "shopify_plus": False, "featured": False, "notable_for": "Size runs across styles = massive SKU matrix. Missing a size on a bestselling style directly tanks conversion."},
    {"name": "Parachute Home", "slug": "parachute-home", "url": "https://parachutehome.com", "category": "home", "description": "Premium bedding, bath, and bedroom essentials. Launched DTC, now 40+ retail stores.", "founded_year": 2014, "employee_count": "200–400", "revenue_tier": "scaleup", "annual_revenue_est": "$80M–$120M", "sku_count": "300–600", "supplier_count": "15–25", "traffic_tier": "large", "location": "Los Angeles, CA", "shopify_plus": True, "featured": False, "notable_for": "Raised $30M. DTC + 40 retail locations means dual inventory streams from the same supplier base. Complex PO coordination."},
    {"name": "Snowe Home", "slug": "snowe-home", "url": "https://snowehome.com", "category": "home", "description": "Direct-to-consumer tabletop, bedding, and bath brand focused on elevated basics.", "founded_year": 2015, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "100–200", "supplier_count": "8–15", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Multi-category home brand sourcing ceramics, textiles, and glass from different countries. Three separate supplier tracks to coordinate."},
    {"name": "Artifox", "slug": "artifox", "url": "https://theartifox.com", "category": "home", "description": "Minimal home office furniture and accessories designed in the US, manufactured overseas.", "founded_year": 2014, "employee_count": "5–10", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "20–40", "supplier_count": "3–6", "traffic_tier": "small", "location": "Cincinnati, OH", "shopify_plus": False, "featured": False, "notable_for": "High-ticket furniture with long production lead times. One late PO can cause 3-month out-of-stocks on $500+ items."},

    # ── Beauty (additional) ────────────────────────────────────────────────
    {"name": "Curie", "slug": "curie", "url": "https://curiebody.com", "category": "beauty", "description": "Clean deodorant and body care brand. Launched in Y Combinator, $5M+ ARR.", "founded_year": 2018, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$3M–$6M", "sku_count": "15–30", "supplier_count": "3–6", "traffic_tier": "small", "location": "San Francisco, CA", "shopify_plus": False, "featured": False, "notable_for": "YC-backed, $5M+ ARR with tiny team. Consumable body care = high reorder frequency. Running out of stock on a subscription item = instant churn."},
    {"name": "Maude", "slug": "maude", "url": "https://getmaude.com", "category": "beauty", "description": "Sexual wellness brand with minimal, modern branding. Lubricants, vibrators, and wellness products.", "founded_year": 2018, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$5M–$10M", "sku_count": "20–40", "supplier_count": "4–8", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Raised $7M. Electronic + consumable SKUs require coordinating two very different supply chains simultaneously."},
    {"name": "Aesop", "slug": "aesop", "url": "https://aesop.com", "category": "beauty", "description": "Iconic Australian skincare and body care brand known for apothecary-style products and store design.", "founded_year": 1987, "employee_count": "500–1000", "revenue_tier": "scaleup", "annual_revenue_est": "$100M+", "sku_count": "80–150", "supplier_count": "10–20", "traffic_tier": "large", "location": "Melbourne, Australia", "shopify_plus": True, "featured": False, "notable_for": "Global DTC + 300+ retail locations. Managing Shopify-sourced inventory alongside retail allocation from shared suppliers."},
    {"name": "Kinship", "slug": "kinship", "url": "https://lovekinship.com", "category": "beauty", "description": "Gen Z-focused clean skincare at accessible price points. Cruelty-free, vegan formulas.", "founded_year": 2019, "employee_count": "10–20", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "20–40", "supplier_count": "3–6", "traffic_tier": "medium", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "DTC + retail (Target, Ulta). Two separate inventory streams, same SKUs. Supplier forecasting must account for both channels simultaneously."},
    {"name": "Herbivore Botanicals", "slug": "herbivore-botanicals", "url": "https://herbivorebotanicals.com", "category": "beauty", "description": "Natural skincare with beautiful, Instagram-worthy packaging. Rose quartz rollers, face oils, serums.", "founded_year": 2011, "employee_count": "25–50", "revenue_tier": "growing", "annual_revenue_est": "$8M–$15M", "sku_count": "40–80", "supplier_count": "6–12", "traffic_tier": "medium", "location": "Seattle, WA", "shopify_plus": False, "featured": False, "notable_for": "Products have distinct packaging components (crystals, glass, accessories) sourced separately. Coordinating formula + packaging suppliers from different countries."},

    # ── Sports (additional) ────────────────────────────────────────────────
    {"name": "Tracksmith", "slug": "tracksmith", "url": "https://tracksmith.com", "category": "sports", "description": "Premium running apparel inspired by the sport's heritage. Performance gear without the tech-bro aesthetic.", "founded_year": 2014, "employee_count": "25–50", "revenue_tier": "growing", "annual_revenue_est": "$10M–$20M", "sku_count": "80–150", "supplier_count": "6–12", "traffic_tier": "medium", "location": "Boston, MA", "shopify_plus": False, "featured": False, "notable_for": "Boston Marathon event drops create massive demand spikes. Advance supplier coordination for limited drops is business-critical."},
    {"name": "Kettle & Fire", "slug": "kettle-fire", "url": "https://kettleandfire.com", "category": "food", "description": "Bone broth brand that made the category mainstream. Chicken, beef, and specialty broths.", "founded_year": 2015, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$20M–$40M", "sku_count": "15–30", "supplier_count": "4–8", "traffic_tier": "medium", "location": "San Francisco, CA", "shopify_plus": False, "featured": False, "notable_for": "High-velocity consumable, subscription model. Raised $8M. DTC + retail channels require coordinated inventory planning from the same protein supplier base."},
    {"name": "Nocs Provisions", "slug": "nocs-provisions", "url": "https://nocsprovisions.com", "category": "sports", "description": "Design-forward binoculars and optics for outdoor adventures. Birdwatching, hiking, and travel.", "founded_year": 2012, "employee_count": "5–10", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "20–40", "supplier_count": "2–4", "traffic_tier": "small", "location": "United States", "shopify_plus": False, "featured": False, "notable_for": "Specialty optics sourced from a single overseas factory. Supply chain concentration risk means any production delay wipes out the whole product line."},
    {"name": "Ciele Athletics", "slug": "ciele-athletics", "url": "https://cieleathletics.com", "category": "sports", "description": "Premium running hats and caps made for performance. Montreal-founded, global cult following.", "founded_year": 2014, "employee_count": "10–25", "revenue_tier": "growing", "annual_revenue_est": "$3M–$7M", "sku_count": "60–120", "supplier_count": "4–8", "traffic_tier": "medium", "location": "Montreal, Canada", "shopify_plus": False, "featured": False, "notable_for": "Colorway-heavy catalog = massive variant tree. Managing hat + apparel replenishment across seasonal drops with long manufacturing lead times."},

    # ── Pet (additional) ───────────────────────────────────────────────────
    {"name": "BarkBox", "slug": "barkbox", "url": "https://barkbox.com", "category": "pets", "description": "Monthly subscription box for dogs. Themed toys and treats delivered monthly. 2M+ subscribers.", "founded_year": 2011, "employee_count": "200–500", "revenue_tier": "scaleup", "annual_revenue_est": "$100M+", "sku_count": "100–200", "supplier_count": "20–40", "traffic_tier": "large", "location": "New York, NY", "shopify_plus": True, "featured": False, "notable_for": "Monthly themed boxes require planning unique SKUs 6+ months ahead with overseas toy and treat manufacturers. Each month is a new inventory challenge."},
    {"name": "West Paw", "slug": "west-paw", "url": "https://westpaw.com", "category": "pets", "description": "US-made durable dog toys and pet accessories. Zogoflex line is known for indestructible quality.", "founded_year": 1996, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$10M–$20M", "sku_count": "60–120", "supplier_count": "6–12", "traffic_tier": "medium", "location": "Bozeman, MT", "shopify_plus": False, "featured": False, "notable_for": "US-manufactured with domestic raw material suppliers. DTC + major retail distribution requires tight inventory segmentation from the same production run."},
    {"name": "The Foggy Dog", "slug": "the-foggy-dog", "url": "https://thefoggydog.com", "category": "pets", "description": "Premium dog accessories with a focus on design. Bandanas, collars, bow ties, and accessories.", "founded_year": 2014, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$1M–$3M", "sku_count": "80–150", "supplier_count": "4–8", "traffic_tier": "small", "location": "United States", "shopify_plus": False, "featured": False, "notable_for": "Seasonal limited-edition drops. Small team managing pattern/colorway complexity across accessory manufacturers."},

    # ── Food (additional) ──────────────────────────────────────────────────
    {"name": "Siete Family Foods", "slug": "siete-family-foods", "url": "https://sietefoods.com", "category": "food", "description": "Grain-free Mexican-American food brand. Tortillas, chips, sauces, and seasonings.", "founded_year": 2014, "employee_count": "100–200", "revenue_tier": "scaleup", "annual_revenue_est": "$100M+", "sku_count": "30–60", "supplier_count": "8–15", "traffic_tier": "large", "location": "Austin, TX", "shopify_plus": True, "featured": False, "notable_for": "Acquired by PepsiCo for $1.2B in 2024. Pre-acquisition: managing grain-free ingredient suppliers across chips, tortillas, and sauces from a small team."},
    {"name": "Magic Spoon", "slug": "magic-spoon", "url": "https://magicspoon.com", "category": "food", "description": "High-protein, low-carb cereal brand targeting adults with nostalgia for childhood flavors.", "founded_year": 2019, "employee_count": "25–50", "revenue_tier": "growing", "annual_revenue_est": "$20M–$40M", "sku_count": "10–20", "supplier_count": "3–6", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Raised $85M. DTC + 35K+ retail doors. Same SKUs, two channels, shared supplier capacity. Allocating inventory between DTC and wholesale while staying in stock everywhere."},
    {"name": "Partake Foods", "slug": "partake-foods", "url": "https://partakefoods.com", "category": "food", "description": "Allergy-friendly snacks free of top 9 allergens. Cookies, pancake mixes, and snack packs.", "founded_year": 2017, "employee_count": "15–30", "revenue_tier": "growing", "annual_revenue_est": "$5M–$15M", "sku_count": "15–30", "supplier_count": "4–8", "traffic_tier": "small", "location": "Newark, NJ", "shopify_plus": False, "featured": False, "notable_for": "Raised $19M. Allergen-free certification = limited qualified suppliers. Supply chain concentration requires tighter PO management than conventional food brands."},
    {"name": "Solely", "slug": "solely", "url": "https://solely.com", "category": "food", "description": "Organic fruit jerky made from single-ingredient whole fruits. Clean snacks with no additives.", "founded_year": 2018, "employee_count": "5–15", "revenue_tier": "growing", "annual_revenue_est": "$2M–$5M", "sku_count": "15–25", "supplier_count": "5–10", "traffic_tier": "small", "location": "Los Angeles, CA", "shopify_plus": False, "featured": False, "notable_for": "Seasonal fruit sourcing means supplier contracts must be placed months in advance. Agricultural supply chain with built-in uncertainty."},

    # ── Health (additional) ────────────────────────────────────────────────
    {"name": "Seed Health", "slug": "seed-health", "url": "https://seed.com", "category": "health", "description": "Science-backed probiotic brand. DS-01 Daily Synbiotic is their flagship product.", "founded_year": 2018, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$30M–$60M", "sku_count": "5–10", "supplier_count": "4–8", "traffic_tier": "large", "location": "Los Angeles, CA", "shopify_plus": True, "featured": False, "notable_for": "Subscription-first with razor-thin SKU count. At scale, even with few SKUs, subscriber forecasting and supplier lead times become critical."},
    {"name": "Thesis", "slug": "thesis", "url": "https://takethesis.com", "category": "health", "description": "Personalized nootropic supplements. Custom formulas based on quiz results.", "founded_year": 2017, "employee_count": "25–50", "revenue_tier": "growing", "annual_revenue_est": "$10M–$20M", "sku_count": "20–40", "supplier_count": "5–10", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Personalized supplement model = unpredictable demand per formula variant. Managing ingredient inventory to cover all possible custom combinations is an operations puzzle."},
    {"name": "Gainful", "slug": "gainful", "url": "https://gainful.com", "category": "health", "description": "Personalized protein powder subscriptions. Custom blends based on fitness goals and dietary needs.", "founded_year": 2017, "employee_count": "20–40", "revenue_tier": "growing", "annual_revenue_est": "$8M–$15M", "sku_count": "30–60", "supplier_count": "5–10", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Acquired by Nestlé. Personalized subscription model: forecasting ingredient demand across dozens of custom protein combinations requires tight ops systems."},
    {"name": "Momentous", "slug": "momentous", "url": "https://livemomentous.com", "category": "health", "description": "NSF-certified sports nutrition brand trusted by pro teams and elite athletes. Protein, omega-3s, creatine.", "founded_year": 2016, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$20M–$40M", "sku_count": "40–80", "supplier_count": "6–12", "traffic_tier": "medium", "location": "San Diego, CA", "shopify_plus": False, "featured": False, "notable_for": "NSF certification requires vetted ingredient suppliers with strict documentation. Managing certified supplier relationships with tight lead times."},

    # ── Accessories / Other ────────────────────────────────────────────────
    {"name": "Dagne Dover", "slug": "dagne-dover", "url": "https://dagnedover.com", "category": "apparel", "description": "Smart, functional bags and accessories designed for women. Totes, backpacks, diaper bags, and organizers.", "founded_year": 2013, "employee_count": "25–50", "revenue_tier": "scaleup", "annual_revenue_est": "$15M–$30M", "sku_count": "100–200", "supplier_count": "6–12", "traffic_tier": "medium", "location": "New York, NY", "shopify_plus": True, "featured": False, "notable_for": "Raised $5M. Multi-material bags (neoprene, leather, hardware) require coordinating 3+ component suppliers per SKU."},
    {"name": "Uppercase Magazine", "slug": "uppercase-magazine", "url": "https://uppercasemagazine.com", "category": "home", "description": "Independent print magazine and stationery brand for the creative community. Journals, planners, art prints.", "founded_year": 2009, "employee_count": "1–5", "revenue_tier": "growing", "annual_revenue_est": "$500K–$1M", "sku_count": "50–100", "supplier_count": "3–6", "traffic_tier": "small", "location": "Calgary, Canada", "shopify_plus": False, "featured": False, "notable_for": "Solo operator managing print + product runs. Classic example of a tiny Shopify merchant drowning in manual supplier POs."},
    {"name": "Baggu", "slug": "baggu", "url": "https://baggu.com", "category": "apparel", "description": "Reusable bag brand known for colorful nylon and canvas bags. Strong cult following, iconic prints.", "founded_year": 2007, "employee_count": "25–50", "revenue_tier": "growing", "annual_revenue_est": "$10M–$20M", "sku_count": "100–200", "supplier_count": "4–8", "traffic_tier": "large", "location": "New York, NY", "shopify_plus": False, "featured": False, "notable_for": "Seasonal print drops + core basics catalog. Managing new print inventory alongside evergreen SKUs from overseas manufacturers."},
    {"name": "Huckberry", "slug": "huckberry", "url": "https://huckberry.com", "category": "apparel", "description": "Curated men's outdoor and adventure gear retailer. Mix of owned brand and curated third-party brands.", "founded_year": 2011, "employee_count": "50–100", "revenue_tier": "scaleup", "annual_revenue_est": "$30M–$60M", "sku_count": "1,000–3,000", "supplier_count": "50–100", "traffic_tier": "large", "location": "San Francisco, CA", "shopify_plus": True, "featured": False, "notable_for": "Multi-brand retailer + private label. Managing purchase orders across 50+ vendor brands plus private label manufacturing simultaneously."},
]


class Command(BaseCommand):
    help = 'Seed the directory with supplier and Shopify store data from US customs records'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            Supplier.objects.all().delete()
            ShopifyStore.objects.all().delete()
            self.stdout.write('Cleared existing directory data.')

        created_suppliers = 0
        for data in SUPPLIERS:
            slug = data.get('slug') or slugify(data['name'])
            country_code = COUNTRY_MAP.get(data['country'], 'OTHER')
            category_code = CAT_MAP.get(data['category'], 'other')

            obj, created = Supplier.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': data['name'],
                    'country': country_code,
                    'category': category_code,
                    'description': data.get('description', ''),
                    'products': data.get('products', ''),
                    'us_importers': data.get('us_importers', 0),
                    'total_shipments': data.get('total_shipments', 0),
                    'annual_shipments': data.get('annual_shipments', 0),
                    'notable_brands': data.get('notable_brands', []),
                    'featured': data.get('featured', False),
                }
            )
            if created:
                created_suppliers += 1

        created_stores = 0
        for data in SHOPIFY_STORES:
            obj, created = ShopifyStore.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'url': data['url'],
                    'category': data['category'],
                    'description': data.get('description', ''),
                    'founded_year': data.get('founded_year'),
                    'employee_count': data.get('employee_count', ''),
                    'revenue_tier': data.get('revenue_tier', ''),
                    'traffic_tier': data.get('traffic_tier', ''),
                    'location': data.get('location', ''),
                    'annual_revenue_est': data.get('annual_revenue_est', ''),
                    'sku_count': data.get('sku_count', ''),
                    'supplier_count': data.get('supplier_count', ''),
                    'notable_for': data.get('notable_for', ''),
                    'shopify_plus': data.get('shopify_plus', False),
                    'featured': data.get('featured', False),
                }
            )
            if created:
                created_stores += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded {created_suppliers} new suppliers ({Supplier.objects.count()} total) '
                f'and {created_stores} new stores ({ShopifyStore.objects.count()} total).'
            )
        )
