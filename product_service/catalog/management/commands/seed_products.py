from django.core.management.base import BaseCommand
from catalog.infrastructure.models import CategoryModel, BrandModel, ProductTypeModel, ProductModel


class Command(BaseCommand):
    help = 'Seed database with 10 categories and ~6-7 products each'

    def handle(self, *args, **options):
        self.stdout.write('Seeding products...')
        self._seed_categories()
        self._seed_brands()
        self._seed_product_types()
        self._seed_products()
        self.stdout.write(self.style.SUCCESS('Done! 10 categories, ~65 products seeded.'))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _cat(self, slug):
        return CategoryModel.objects.get(slug=slug)

    def _brand(self, name):
        return BrandModel.objects.get(name=name)

    def _pt(self, name):
        return ProductTypeModel.objects.get(name=name)

    def _make(self, data):
        obj, created = ProductModel.objects.get_or_create(
            sku=data['sku'], defaults=data
        )
        if created:
            self.stdout.write(f'  + {obj.name}')

    # ── seed methods ─────────────────────────────────────────────────────────

    def _seed_categories(self):
        cats = [
            ('Electronics',     'electronics'),
            ('Fashion',         'fashion'),
            ('Home & Garden',   'home-garden'),
            ('Sports',          'sports'),
            ('Books',           'books'),
            ('Beauty & Health', 'beauty-health'),
            ('Toys & Games',    'toys-games'),
            ('Automotive',      'automotive'),
            ('Food & Grocery',  'food-grocery'),
            ('Pet Supplies',    'pet-supplies'),
        ]
        for name, slug in cats:
            c, created = CategoryModel.objects.get_or_create(slug=slug, defaults={'name': name})
            if created:
                self.stdout.write(f'Category: {name}')

    def _seed_brands(self):
        brands = [
            ('Apple',       'USA'),
            ('Samsung',     'South Korea'),
            ('Nike',        'USA'),
            ('Adidas',      'Germany'),
            ('Sony',        'Japan'),
            ('IKEA',        'Sweden'),
            ('Zara',        'Spain'),
            ('Lego',        'Denmark'),
            ('Bosch',       'Germany'),
            ('LOreal',      'France'),
            ('Pedigree',    'USA'),
            ('Michelin',    'France'),
            ('Penguin',     'UK'),
            ('Nestlé',      'Switzerland'),
            ('Hasbro',      'USA'),
        ]
        for name, country in brands:
            BrandModel.objects.get_or_create(name=name, defaults={'country': country})

    def _seed_product_types(self):
        pts = [
            ('Smartphone',   'Mobile phones'),
            ('Laptop',       'Portable computers'),
            ('Headphones',   'Audio devices'),
            ('Tablet',       'Touchscreen tablets'),
            ('Smartwatch',   'Wearable devices'),
            ('TV',           'Television displays'),
            ('Camera',       'Photography devices'),
            ('T-Shirt',      'Casual tops'),
            ('Sneakers',     'Athletic footwear'),
            ('Jacket',       'Outerwear'),
            ('Dress',        'Women dresses'),
            ('Jeans',        'Denim pants'),
            ('Furniture',    'Home furniture'),
            ('Cookware',     'Kitchen tools'),
            ('Bedding',      'Bed linen'),
            ('Garden Tool',  'Outdoor gardening'),
            ('Fitness',      'Exercise equipment'),
            ('Ball',         'Sports balls'),
            ('Bicycle',      'Cycling'),
            ('Book',         'Printed books'),
            ('Skincare',     'Skin products'),
            ('Makeup',       'Cosmetics'),
            ('Supplement',   'Health supplements'),
            ('Board Game',   'Tabletop games'),
            ('Action Figure','Collectible figures'),
            ('Building Set', 'Construction toys'),
            ('Car Part',     'Vehicle components'),
            ('Car Care',     'Vehicle maintenance'),
            ('Snack',        'Food snacks'),
            ('Beverage',     'Drinks'),
            ('Pet Food',     'Animal nutrition'),
            ('Pet Toy',      'Animal toys'),
            ('Pet Care',     'Animal grooming'),
        ]
        for name, desc in pts:
            ProductTypeModel.objects.get_or_create(name=name, defaults={'description': desc})

    def _seed_products(self):
        self._electronics()
        self._fashion()
        self._home_garden()
        self._sports()
        self._books()
        self._beauty_health()
        self._toys_games()
        self._automotive()
        self._food_grocery()
        self._pet_supplies()

    # ── Electronics (7 products) ─────────────────────────────────────────────

    def _electronics(self):
        e = self._cat('electronics')
        self._make({'name': 'iPhone 15 Pro', 'sku': 'IPHONE15PRO', 'price': 999.99, 'stock': 50,
            'description': 'Titanium design, A17 Pro chip, 48MP camera system.',
            'image': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-1inch-naturaltitanium?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1692845702708',
            'category': e, 'brand': self._brand('Apple'), 'product_type': self._pt('Smartphone'),
            'attributes': {'storage': '128GB', 'color': 'Natural Titanium', 'screen': '6.1"'}})
        self._make({'name': 'Samsung Galaxy S24 Ultra', 'sku': 'GALAXYS24U', 'price': 1299.99, 'stock': 40,
            'description': 'Galaxy AI, 200MP camera, built-in S Pen.',
            'image': 'https://images.samsung.com/is/image/samsung/p6pim/levant/2401/gallery/levant-galaxy-s24-ultra-s928-sm-s928bzaceub-thumb-539573520',
            'category': e, 'brand': self._brand('Samsung'), 'product_type': self._pt('Smartphone'),
            'attributes': {'storage': '256GB', 'color': 'Titanium Black', 'screen': '6.8"'}})
        self._make({'name': 'MacBook Pro 14"', 'sku': 'MBP14M3', 'price': 1999.99, 'stock': 25,
            'description': 'M3 Pro chip, Liquid Retina XDR display, 18GB RAM.',
            'image': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spacegray-select-202310?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1697311054290',
            'category': e, 'brand': self._brand('Apple'), 'product_type': self._pt('Laptop'),
            'attributes': {'chip': 'M3 Pro', 'ram': '18GB', 'storage': '512GB SSD'}})
        self._make({'name': 'Sony WH-1000XM5', 'sku': 'SONYWH1000XM5', 'price': 349.99, 'stock': 60,
            'description': 'Industry-leading noise cancellation, 30h battery.',
            'image': 'https://www.sony.com/image/5d02da5df552836db894c04c7e37c3b8?fmt=pjpeg&wid=660&bgcolor=FFFFFF&bgc=FFFFFF',
            'category': e, 'brand': self._brand('Sony'), 'product_type': self._pt('Headphones'),
            'attributes': {'type': 'Over-ear', 'bluetooth': '5.2', 'battery': '30h'}})
        self._make({'name': 'iPad Air M2', 'sku': 'IPADAIRM2', 'price': 599.99, 'stock': 45,
            'description': 'M2 chip, 10.9" Liquid Retina, USB-C.',
            'image': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-air-select-wifi-blue-202203?wid=470&hei=556&fmt=png-alpha&.v=1645065732688',
            'category': e, 'brand': self._brand('Apple'), 'product_type': self._pt('Tablet'),
            'attributes': {'chip': 'M2', 'storage': '64GB', 'color': 'Sky Blue'}})
        self._make({'name': 'Samsung 55" 4K QLED TV', 'sku': 'SAMSUNGQLED55', 'price': 799.99, 'stock': 20,
            'description': 'Quantum Dot technology, 120Hz, Smart TV.',
            'image': 'https://images.samsung.com/is/image/samsung/p6pim/uk/qa55q80cauxua/gallery/uk-qled-q80c-qa55q80cauxua-frontblack-536839855',
            'category': e, 'brand': self._brand('Samsung'), 'product_type': self._pt('TV'),
            'attributes': {'size': '55"', 'resolution': '4K', 'refresh': '120Hz'}})
        self._make({'name': 'Sony Alpha A7 IV', 'sku': 'SONYA7IV', 'price': 2499.99, 'stock': 15,
            'description': 'Full-frame mirrorless, 33MP, 4K 60fps video.',
            'image': 'https://www.sony.com/image/a4b4e4e4e4e4e4e4e4e4e4e4e4e4e4e4?fmt=pjpeg&wid=660',
            'category': e, 'brand': self._brand('Sony'), 'product_type': self._pt('Camera'),
            'attributes': {'sensor': '33MP Full-frame', 'video': '4K 60fps', 'mount': 'E-mount'}})

    # ── Fashion (7 products) ─────────────────────────────────────────────────

    def _fashion(self):
        f = self._cat('fashion')
        self._make({'name': 'Nike Air Max 270', 'sku': 'AIRMAX270', 'price': 150.00, 'stock': 120,
            'description': 'Max Air heel unit, breathable mesh upper.',
            'image': 'https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/awjogtdnqxniqqk0wpgf/air-max-270-shoes-KkLcGR.png',
            'category': f, 'brand': self._brand('Nike'), 'product_type': self._pt('Sneakers'),
            'attributes': {'color': 'Black/White', 'material': 'Mesh', 'sole': 'Air Max'}})
        self._make({'name': 'Adidas Ultraboost 23', 'sku': 'ULTRABOOST23', 'price': 190.00, 'stock': 80,
            'description': 'Boost midsole, Primeknit+ upper, Continental rubber.',
            'image': 'https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/fbaf991a78bc4896a3e9ad7800abcec6_9366/Ultraboost_Light_Running_Shoes_White_HQ6351_01_standard.jpg',
            'category': f, 'brand': self._brand('Adidas'), 'product_type': self._pt('Sneakers'),
            'attributes': {'color': 'Cloud White', 'technology': 'Boost', 'upper': 'Primeknit+'}})
        self._make({'name': 'Zara Slim Fit Jeans', 'sku': 'ZARAJEANS01', 'price': 49.99, 'stock': 200,
            'description': 'Classic slim fit, stretch denim, 5-pocket design.',
            'image': 'https://static.zara.net/assets/public/0a3b/1234/abcd5678/slim-jeans.jpg?ts=1700000000000&w=563',
            'category': f, 'brand': self._brand('Zara'), 'product_type': self._pt('Jeans'),
            'attributes': {'fit': 'Slim', 'color': 'Dark Blue', 'material': 'Stretch Denim'}})
        self._make({'name': 'Nike Dri-FIT Training Tee', 'sku': 'NIKEDRIFIT01', 'price': 35.00, 'stock': 300,
            'description': 'Sweat-wicking fabric, relaxed fit for training.',
            'image': 'https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/61734ec7-dad8-40f3-9b95-c7500939150a/dri-fit-miler-running-top-JgTj3B.png',
            'category': f, 'brand': self._brand('Nike'), 'product_type': self._pt('T-Shirt'),
            'attributes': {'color': 'Black', 'material': 'Polyester', 'fit': 'Relaxed'}})
        self._make({'name': 'Adidas Tiro 23 Jacket', 'sku': 'TIRO23JACKET', 'price': 65.00, 'stock': 90,
            'description': 'Lightweight training jacket, zip pockets.',
            'image': 'https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/tiro23-jacket-black.jpg',
            'category': f, 'brand': self._brand('Adidas'), 'product_type': self._pt('Jacket'),
            'attributes': {'color': 'Black/White', 'material': 'Recycled Polyester', 'closure': 'Full-zip'}})
        self._make({'name': 'Zara Floral Midi Dress', 'sku': 'ZARADRESS01', 'price': 59.99, 'stock': 150,
            'description': 'Floral print, V-neck, midi length, flowy fabric.',
            'image': 'https://static.zara.net/assets/public/floral-midi-dress.jpg?ts=1700000000000&w=563',
            'category': f, 'brand': self._brand('Zara'), 'product_type': self._pt('Dress'),
            'attributes': {'color': 'Multicolor', 'length': 'Midi', 'neckline': 'V-neck'}})
        self._make({'name': 'Nike Air Force 1 Low', 'sku': 'AF1LOW01', 'price': 110.00, 'stock': 100,
            'description': 'Iconic basketball shoe, leather upper, Air cushioning.',
            'image': 'https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/b7d9211c-26e7-431a-ac24-b0540fb3c00f/air-force-1-07-shoes-WjnRLl.png',
            'category': f, 'brand': self._brand('Nike'), 'product_type': self._pt('Sneakers'),
            'attributes': {'color': 'White', 'material': 'Leather', 'style': 'Low-top'}})

    # ── Home & Garden (6 products) ───────────────────────────────────────────

    def _home_garden(self):
        h = self._cat('home-garden')
        self._make({'name': 'IKEA KALLAX Shelf Unit', 'sku': 'IKEA-KALLAX-4X4', 'price': 179.99, 'stock': 30,
            'description': '4x4 cube shelf, white, versatile storage solution.',
            'image': 'https://www.ikea.com/us/en/images/products/kallax-shelf-unit-white__0644757_pe702938_s5.jpg',
            'category': h, 'brand': self._brand('IKEA'), 'product_type': self._pt('Furniture'),
            'attributes': {'color': 'White', 'dimensions': '147x147cm', 'compartments': '16'}})
        self._make({'name': 'IKEA POÄNG Armchair', 'sku': 'IKEA-POANG-01', 'price': 129.99, 'stock': 25,
            'description': 'Bent birch frame, cushioned seat, timeless design.',
            'image': 'https://www.ikea.com/us/en/images/products/poaeng-armchair-birch-veneer-knisa-light-beige__0938160_pe793677_s5.jpg',
            'category': h, 'brand': self._brand('IKEA'), 'product_type': self._pt('Furniture'),
            'attributes': {'material': 'Birch veneer', 'color': 'Light Beige', 'max_load': '110kg'}})
        self._make({'name': 'Bosch Cordless Drill GSR 18V', 'sku': 'BOSCH-GSR18V', 'price': 149.99, 'stock': 40,
            'description': '18V brushless motor, 2-speed gearbox, LED light.',
            'image': 'https://www.bosch-professional.com/binary/content/pictures/industries/products/gsr-18v-55-06019h5200_anz.jpg',
            'category': h, 'brand': self._brand('Bosch'), 'product_type': self._pt('Garden Tool'),
            'attributes': {'voltage': '18V', 'torque': '55Nm', 'chuck': '13mm'}})
        self._make({'name': 'IKEA HEMNES Bed Frame', 'sku': 'IKEA-HEMNES-Q', 'price': 299.99, 'stock': 15,
            'description': 'Queen size, solid pine, classic Scandinavian style.',
            'image': 'https://www.ikea.com/us/en/images/products/hemnes-bed-frame-white-stain__0637431_pe698416_s5.jpg',
            'category': h, 'brand': self._brand('IKEA'), 'product_type': self._pt('Furniture'),
            'attributes': {'size': 'Queen', 'material': 'Solid Pine', 'color': 'White Stain'}})
        self._make({'name': 'Bosch Garden Hose 20m', 'sku': 'BOSCH-HOSE20', 'price': 39.99, 'stock': 80,
            'description': 'Kink-resistant, 20m, with spray gun.',
            'image': 'https://www.bosch-diy.com/content/dam/bosch-diy/products/garden/hose-20m.jpg',
            'category': h, 'brand': self._brand('Bosch'), 'product_type': self._pt('Garden Tool'),
            'attributes': {'length': '20m', 'diameter': '13mm', 'includes': 'Spray gun'}})
        self._make({'name': 'IKEA MALM 6-Drawer Dresser', 'sku': 'IKEA-MALM-6D', 'price': 249.99, 'stock': 20,
            'description': '6 spacious drawers, smooth-running, white finish.',
            'image': 'https://www.ikea.com/us/en/images/products/malm-6-drawer-dresser-white__0625609_pe692249_s5.jpg',
            'category': h, 'brand': self._brand('IKEA'), 'product_type': self._pt('Furniture'),
            'attributes': {'color': 'White', 'drawers': '6', 'dimensions': '80x123cm'}})

    # ── Sports (7 products) ──────────────────────────────────────────────────

    def _sports(self):
        s = self._cat('sports')
        self._make({'name': 'Nike Pro Yoga Mat', 'sku': 'NIKE-YOGAMAT', 'price': 45.00, 'stock': 150,
            'description': 'Non-slip surface, 4mm thick, carry strap included.',
            'image': 'https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/yoga-mat-3mm-9in1.png',
            'category': s, 'brand': self._brand('Nike'), 'product_type': self._pt('Fitness'),
            'attributes': {'thickness': '4mm', 'material': 'NBR Foam', 'size': '183x61cm'}})
        self._make({'name': 'Adidas Soccer Ball Size 5', 'sku': 'ADIDAS-BALL5', 'price': 29.99, 'stock': 200,
            'description': 'FIFA quality, thermally bonded, all-weather.',
            'image': 'https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/tango-soccer-ball.jpg',
            'category': s, 'brand': self._brand('Adidas'), 'product_type': self._pt('Ball'),
            'attributes': {'size': '5', 'surface': 'All-weather', 'certification': 'FIFA Quality'}})
        self._make({'name': 'Nike Resistance Bands Set', 'sku': 'NIKE-BANDS5', 'price': 25.00, 'stock': 300,
            'description': '5 resistance levels, latex-free, door anchor included.',
            'image': 'https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/resistance-bands-set.png',
            'category': s, 'brand': self._brand('Nike'), 'product_type': self._pt('Fitness'),
            'attributes': {'levels': '5', 'material': 'Latex-free TPE', 'includes': 'Door anchor + bag'}})
        self._make({'name': 'Adidas Predator Football Boots', 'sku': 'ADIDAS-PRED24', 'price': 220.00, 'stock': 60,
            'description': 'Controlframe outsole, Demonskin texture, firm ground.',
            'image': 'https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/predator-accuracy-fg-boots.jpg',
            'category': s, 'brand': self._brand('Adidas'), 'product_type': self._pt('Sneakers'),
            'attributes': {'surface': 'Firm Ground', 'technology': 'Demonskin', 'color': 'Black/Red'}})
        self._make({'name': 'Trek FX 3 Disc Hybrid Bike', 'sku': 'TREK-FX3DISC', 'price': 849.99, 'stock': 10,
            'description': 'Lightweight Alpha Gold Aluminum, hydraulic disc brakes.',
            'image': 'https://trek.scene7.com/is/image/TrekBicycleProducts/FX3Disc_23_35823_A_Primary',
            'category': s, 'brand': self._brand('Nike'), 'product_type': self._pt('Bicycle'),
            'attributes': {'frame': 'Aluminum', 'brakes': 'Hydraulic Disc', 'gears': '24-speed'}})
        self._make({'name': 'Nike Metcon 9 Training Shoes', 'sku': 'NIKE-METCON9', 'price': 130.00, 'stock': 75,
            'description': 'Stable base for lifting, flexible forefoot for running.',
            'image': 'https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/metcon-9-workout-shoes.png',
            'category': s, 'brand': self._brand('Nike'), 'product_type': self._pt('Sneakers'),
            'attributes': {'color': 'White/Black', 'sole': 'Rubber', 'closure': 'Lace-up'}})
        self._make({'name': 'Adidas Gym Duffel Bag', 'sku': 'ADIDAS-DUFFEL', 'price': 55.00, 'stock': 100,
            'description': '40L capacity, wet/dry compartment, adjustable strap.',
            'image': 'https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/gym-duffel-bag-medium.jpg',
            'category': s, 'brand': self._brand('Adidas'), 'product_type': self._pt('Fitness'),
            'attributes': {'capacity': '40L', 'material': 'Polyester', 'color': 'Black'}})

    # ── Books (6 products) ───────────────────────────────────────────────────

    def _books(self):
        b = self._cat('books')
        self._make({'name': 'Clean Code – Robert C. Martin', 'sku': 'BOOK-CLEANCODE', 'price': 35.99, 'stock': 200,
            'description': 'A handbook of agile software craftsmanship.',
            'image': 'https://m.media-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg',
            'category': b, 'brand': self._brand('Penguin'), 'product_type': self._pt('Book'),
            'attributes': {'author': 'Robert C. Martin', 'pages': '431', 'language': 'English'}})
        self._make({'name': 'The Pragmatic Programmer', 'sku': 'BOOK-PRAGPROG', 'price': 39.99, 'stock': 150,
            'description': 'Your journey to mastery, 20th anniversary edition.',
            'image': 'https://m.media-amazon.com/images/I/41as+WafrFL._SX376_BO1,204,203,200_.jpg',
            'category': b, 'brand': self._brand('Penguin'), 'product_type': self._pt('Book'),
            'attributes': {'author': 'Hunt & Thomas', 'pages': '352', 'edition': '20th Anniversary'}})
        self._make({'name': 'Atomic Habits – James Clear', 'sku': 'BOOK-ATOMICHAB', 'price': 18.99, 'stock': 300,
            'description': 'Tiny changes, remarkable results. #1 NYT bestseller.',
            'image': 'https://m.media-amazon.com/images/I/513Y5o-DYtL._SX329_BO1,204,203,200_.jpg',
            'category': b, 'brand': self._brand('Penguin'), 'product_type': self._pt('Book'),
            'attributes': {'author': 'James Clear', 'pages': '320', 'genre': 'Self-help'}})
        self._make({'name': 'Designing Data-Intensive Applications', 'sku': 'BOOK-DDIA', 'price': 49.99, 'stock': 100,
            'description': 'The big ideas behind reliable, scalable systems.',
            'image': 'https://m.media-amazon.com/images/I/51ZSpMl1-LL._SX379_BO1,204,203,200_.jpg',
            'category': b, 'brand': self._brand('Penguin'), 'product_type': self._pt('Book'),
            'attributes': {'author': 'Martin Kleppmann', 'pages': '616', 'topic': 'Distributed Systems'}})
        self._make({'name': 'The Lean Startup – Eric Ries', 'sku': 'BOOK-LEANSTART', 'price': 16.99, 'stock': 180,
            'description': 'How constant innovation creates radically successful businesses.',
            'image': 'https://m.media-amazon.com/images/I/51T-sMqSMiL._SX329_BO1,204,203,200_.jpg',
            'category': b, 'brand': self._brand('Penguin'), 'product_type': self._pt('Book'),
            'attributes': {'author': 'Eric Ries', 'pages': '336', 'genre': 'Business'}})
        self._make({'name': 'Deep Learning – Goodfellow et al.', 'sku': 'BOOK-DEEPLEARN', 'price': 59.99, 'stock': 80,
            'description': 'The definitive textbook on deep learning by MIT Press.',
            'image': 'https://m.media-amazon.com/images/I/61fim5QqaqL._SX379_BO1,204,203,200_.jpg',
            'category': b, 'brand': self._brand('Penguin'), 'product_type': self._pt('Book'),
            'attributes': {'author': 'Goodfellow, Bengio, Courville', 'pages': '800', 'topic': 'AI/ML'}})

    # ── Beauty & Health (7 products) ─────────────────────────────────────────

    def _beauty_health(self):
        bh = self._cat('beauty-health')
        self._make({'name': "L'Oréal Revitalift Serum", 'sku': 'LOREAL-REVIT01', 'price': 29.99, 'stock': 200,
            'description': '1.5% pure hyaluronic acid, plumps and replumps skin.',
            'image': 'https://www.loreal-paris.co.uk/-/media/project/loreal/brand-sites/oap/emea/uk/products/skincare/revitalift/revitalift-1-5-pure-hyaluronic-acid-serum-30ml.png',
            'category': bh, 'brand': self._brand('LOreal'), 'product_type': self._pt('Skincare'),
            'attributes': {'volume': '30ml', 'key_ingredient': 'Hyaluronic Acid', 'skin_type': 'All'}})
        self._make({'name': "L'Oréal True Match Foundation", 'sku': 'LOREAL-TMATCH01', 'price': 14.99, 'stock': 300,
            'description': 'SPF 17, 24h hydration, 45 shades.',
            'image': 'https://www.loreal-paris.co.uk/-/media/project/loreal/brand-sites/oap/emea/uk/products/makeup/face/foundation/true-match-foundation.png',
            'category': bh, 'brand': self._brand('LOreal'), 'product_type': self._pt('Makeup'),
            'attributes': {'coverage': 'Medium', 'finish': 'Natural', 'SPF': '17'}})
        self._make({'name': "L'Oréal Elvive Shampoo 400ml", 'sku': 'LOREAL-ELVIVE01', 'price': 8.99, 'stock': 500,
            'description': 'Extraordinary Oil, nourishes dry and dull hair.',
            'image': 'https://www.loreal-paris.co.uk/-/media/project/loreal/brand-sites/oap/emea/uk/products/haircare/elvive/extraordinary-oil-shampoo.png',
            'category': bh, 'brand': self._brand('LOreal'), 'product_type': self._pt('Skincare'),
            'attributes': {'volume': '400ml', 'hair_type': 'Dry/Dull', 'key_ingredient': 'Extraordinary Oil'}})
        self._make({'name': 'Vitamin C 1000mg Supplement', 'sku': 'VITC-1000MG', 'price': 12.99, 'stock': 400,
            'description': '90 tablets, immune support, antioxidant protection.',
            'image': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&q=80',
            'category': bh, 'brand': self._brand('LOreal'), 'product_type': self._pt('Supplement'),
            'attributes': {'dosage': '1000mg', 'count': '90 tablets', 'form': 'Tablet'}})
        self._make({'name': 'Omega-3 Fish Oil 1000mg', 'sku': 'OMEGA3-1000', 'price': 19.99, 'stock': 250,
            'description': 'EPA & DHA, heart and brain health, 120 softgels.',
            'image': 'https://images.unsplash.com/photo-1550572017-edd951b55104?w=400&q=80',
            'category': bh, 'brand': self._brand('LOreal'), 'product_type': self._pt('Supplement'),
            'attributes': {'dosage': '1000mg', 'count': '120 softgels', 'EPA_DHA': '300mg'}})
        self._make({'name': "L'Oréal Mascara Voluminous", 'sku': 'LOREAL-MASC01', 'price': 11.99, 'stock': 350,
            'description': 'Up to 5x more volume, buildable, smudge-proof.',
            'image': 'https://www.loreal-paris.co.uk/-/media/project/loreal/brand-sites/oap/emea/uk/products/makeup/eyes/mascara/voluminous-mascara.png',
            'category': bh, 'brand': self._brand('LOreal'), 'product_type': self._pt('Makeup'),
            'attributes': {'color': 'Blackest Black', 'formula': 'Smudge-proof', 'brush': 'Curved'}})
        self._make({'name': 'Electric Toothbrush Pro 3000', 'sku': 'ORAL-PRO3000', 'price': 69.99, 'stock': 80,
            'description': '3 cleaning modes, 2-min timer, 2-week battery.',
            'image': 'https://images.unsplash.com/photo-1559591937-abc8a8b8b8b8?w=400&q=80',
            'category': bh, 'brand': self._brand('Bosch'), 'product_type': self._pt('Skincare'),
            'attributes': {'modes': '3', 'battery': '2 weeks', 'timer': '2 min'}})

    # ── Toys & Games (6 products) ────────────────────────────────────────────

    def _toys_games(self):
        t = self._cat('toys-games')
        self._make({'name': 'LEGO Technic Bugatti Chiron', 'sku': 'LEGO-42083', 'price': 349.99, 'stock': 30,
            'description': '3599 pieces, 1:8 scale, working W16 engine.',
            'image': 'https://www.lego.com/cdn/cs/set/assets/blt8e2f8e4e4e4e4e4e/42083_alt1.jpg',
            'category': t, 'brand': self._brand('Lego'), 'product_type': self._pt('Building Set'),
            'attributes': {'pieces': '3599', 'scale': '1:8', 'age': '16+'}})
        self._make({'name': 'LEGO City Police Station', 'sku': 'LEGO-60316', 'price': 199.99, 'stock': 50,
            'description': '668 pieces, 5 minifigures, jail cell and garage.',
            'image': 'https://www.lego.com/cdn/cs/set/assets/blt1234567890abcdef/60316_alt1.jpg',
            'category': t, 'brand': self._brand('Lego'), 'product_type': self._pt('Building Set'),
            'attributes': {'pieces': '668', 'minifigures': '5', 'age': '6+'}})
        self._make({'name': 'Hasbro Monopoly Classic', 'sku': 'HASBRO-MONO01', 'price': 24.99, 'stock': 150,
            'description': 'Classic board game, 2-8 players, ages 8+.',
            'image': 'https://images.unsplash.com/photo-1611996575749-79a3a250f948?w=400&q=80',
            'category': t, 'brand': self._brand('Hasbro'), 'product_type': self._pt('Board Game'),
            'attributes': {'players': '2-8', 'age': '8+', 'duration': '60-180 min'}})
        self._make({'name': 'Hasbro Scrabble Deluxe', 'sku': 'HASBRO-SCRAB01', 'price': 34.99, 'stock': 100,
            'description': 'Rotating board, premium tiles, 2-4 players.',
            'image': 'https://images.unsplash.com/photo-1632501641765-e568d28b0015?w=400&q=80',
            'category': t, 'brand': self._brand('Hasbro'), 'product_type': self._pt('Board Game'),
            'attributes': {'players': '2-4', 'age': '10+', 'tiles': '100'}})
        self._make({'name': 'Marvel Spider-Man Action Figure 30cm', 'sku': 'MARVEL-SPIDEY30', 'price': 29.99, 'stock': 200,
            'description': '30cm articulated figure, 16 points of articulation.',
            'image': 'https://images.unsplash.com/photo-1608889175123-8ee362201f81?w=400&q=80',
            'category': t, 'brand': self._brand('Hasbro'), 'product_type': self._pt('Action Figure'),
            'attributes': {'height': '30cm', 'articulation': '16 points', 'age': '4+'}})
        self._make({'name': 'LEGO Star Wars Millennium Falcon', 'sku': 'LEGO-75192', 'price': 849.99, 'stock': 15,
            'description': '7541 pieces, most detailed LEGO Star Wars set ever.',
            'image': 'https://www.lego.com/cdn/cs/set/assets/blt75192milleniumfalcon/75192_alt1.jpg',
            'category': t, 'brand': self._brand('Lego'), 'product_type': self._pt('Building Set'),
            'attributes': {'pieces': '7541', 'minifigures': '4', 'age': '16+'}})

    # ── Automotive (6 products) ──────────────────────────────────────────────

    def _automotive(self):
        a = self._cat('automotive')
        self._make({'name': 'Michelin Pilot Sport 4S 245/40R18', 'sku': 'MICH-PS4S-24540R18', 'price': 189.99, 'stock': 40,
            'description': 'Ultra-high performance summer tyre, dry and wet grip.',
            'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80',
            'category': a, 'brand': self._brand('Michelin'), 'product_type': self._pt('Car Part'),
            'attributes': {'size': '245/40R18', 'season': 'Summer', 'load_index': '97Y'}})
        self._make({'name': 'Bosch S5 Car Battery 74Ah', 'sku': 'BOSCH-S5-74AH', 'price': 129.99, 'stock': 35,
            'description': '74Ah, 750A CCA, maintenance-free, 4-year warranty.',
            'image': 'https://images.unsplash.com/photo-1609592806596-b8d7a49f4a8a?w=400&q=80',
            'category': a, 'brand': self._brand('Bosch'), 'product_type': self._pt('Car Part'),
            'attributes': {'capacity': '74Ah', 'CCA': '750A', 'warranty': '4 years'}})
        self._make({'name': 'Michelin CrossClimate 2 205/55R16', 'sku': 'MICH-CC2-20555R16', 'price': 149.99, 'stock': 60,
            'description': 'All-season tyre, A-rated wet grip, 3PMSF certified.',
            'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80',
            'category': a, 'brand': self._brand('Michelin'), 'product_type': self._pt('Car Part'),
            'attributes': {'size': '205/55R16', 'season': 'All-season', 'wet_grip': 'A'}})
        self._make({'name': 'Bosch Aerotwin Wiper Blades 600mm', 'sku': 'BOSCH-AERO600', 'price': 24.99, 'stock': 200,
            'description': 'Flat blade design, even pressure, streak-free.',
            'image': 'https://images.unsplash.com/photo-1609592806596-b8d7a49f4a8a?w=400&q=80',
            'category': a, 'brand': self._brand('Bosch'), 'product_type': self._pt('Car Part'),
            'attributes': {'length': '600mm', 'type': 'Flat/Aerotwin', 'fit': 'Universal'}})
        self._make({'name': 'Meguiars Ultimate Liquid Wax', 'sku': 'MEG-ULTWAX473', 'price': 22.99, 'stock': 150,
            'description': 'Synthetic polymer wax, deep gloss, 473ml.',
            'image': 'https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=400&q=80',
            'category': a, 'brand': self._brand('Bosch'), 'product_type': self._pt('Car Care'),
            'attributes': {'volume': '473ml', 'type': 'Liquid Wax', 'finish': 'High Gloss'}})
        self._make({'name': 'Bosch Oil Filter F026407006', 'sku': 'BOSCH-OF-F026', 'price': 9.99, 'stock': 500,
            'description': 'OEM quality, fits VW/Audi/Skoda/Seat 1.4-2.0 TSI.',
            'image': 'https://images.unsplash.com/photo-1609592806596-b8d7a49f4a8a?w=400&q=80',
            'category': a, 'brand': self._brand('Bosch'), 'product_type': self._pt('Car Part'),
            'attributes': {'OEM': 'F026407006', 'fits': 'VW/Audi 1.4-2.0 TSI', 'type': 'Spin-on'}})

    # ── Food & Grocery (6 products) ──────────────────────────────────────────

    def _food_grocery(self):
        fg = self._cat('food-grocery')
        self._make({'name': "Nestlé KitKat Chunky 40g", 'sku': 'NESTLE-KITKAT40', 'price': 1.49, 'stock': 1000,
            'description': 'Thick milk chocolate bar with crispy wafer.',
            'image': 'https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=400&q=80',
            'category': fg, 'brand': self._brand('Nestlé'), 'product_type': self._pt('Snack'),
            'attributes': {'weight': '40g', 'flavor': 'Milk Chocolate', 'allergens': 'Milk, Wheat'}})
        self._make({'name': "Nestlé Nescafé Gold 200g", 'sku': 'NESTLE-NESCAFE200', 'price': 8.99, 'stock': 500,
            'description': 'Premium instant coffee, rich and smooth taste.',
            'image': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&q=80',
            'category': fg, 'brand': self._brand('Nestlé'), 'product_type': self._pt('Beverage'),
            'attributes': {'weight': '200g', 'type': 'Instant Coffee', 'roast': 'Medium'}})
        self._make({'name': "Nestlé Milo 400g", 'sku': 'NESTLE-MILO400', 'price': 5.99, 'stock': 600,
            'description': 'Chocolate malt drink, energy for active kids.',
            'image': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400&q=80',
            'category': fg, 'brand': self._brand('Nestlé'), 'product_type': self._pt('Beverage'),
            'attributes': {'weight': '400g', 'type': 'Malt Drink', 'vitamins': 'B2, B3, B6, B12'}})
        self._make({'name': "Nestlé Maggi 2-Minute Noodles 12-pack", 'sku': 'NESTLE-MAGGI12', 'price': 4.99, 'stock': 800,
            'description': 'Quick cook noodles, chicken flavor, 12 x 70g.',
            'image': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80',
            'category': fg, 'brand': self._brand('Nestlé'), 'product_type': self._pt('Snack'),
            'attributes': {'count': '12 packs', 'weight': '70g each', 'flavor': 'Chicken'}})
        self._make({'name': "Nestlé Pure Life Water 1.5L 6-pack", 'sku': 'NESTLE-WATER6', 'price': 3.99, 'stock': 1000,
            'description': 'Natural spring water, 6 x 1.5L bottles.',
            'image': 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&q=80',
            'category': fg, 'brand': self._brand('Nestlé'), 'product_type': self._pt('Beverage'),
            'attributes': {'volume': '1.5L x 6', 'type': 'Spring Water', 'pH': '7.4'}})
        self._make({'name': "Nestlé Cheerios Honey Nut 375g", 'sku': 'NESTLE-CHEERIOS375', 'price': 4.49, 'stock': 400,
            'description': 'Whole grain oat cereal, honey nut flavor.',
            'image': 'https://images.unsplash.com/photo-1517093157656-b9eccef91cb1?w=400&q=80',
            'category': fg, 'brand': self._brand('Nestlé'), 'product_type': self._pt('Snack'),
            'attributes': {'weight': '375g', 'flavor': 'Honey Nut', 'grain': 'Whole Grain Oat'}})

    # ── Pet Supplies (6 products) ────────────────────────────────────────────

    def _pet_supplies(self):
        p = self._cat('pet-supplies')
        self._make({'name': 'Pedigree Adult Dry Dog Food 15kg', 'sku': 'PEDIGREE-DRY15', 'price': 34.99, 'stock': 200,
            'description': 'Complete nutrition, chicken & vegetables, 15kg bag.',
            'image': 'https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=400&q=80',
            'category': p, 'brand': self._brand('Pedigree'), 'product_type': self._pt('Pet Food'),
            'attributes': {'weight': '15kg', 'flavor': 'Chicken & Vegetables', 'life_stage': 'Adult'}})
        self._make({'name': 'Pedigree Dentastix Daily 28-pack', 'sku': 'PEDIGREE-DENTA28', 'price': 12.99, 'stock': 400,
            'description': 'Reduces tartar build-up, X-shape design, 28 sticks.',
            'image': 'https://images.unsplash.com/photo-1601758124510-52d02ddb7cbd?w=400&q=80',
            'category': p, 'brand': self._brand('Pedigree'), 'product_type': self._pt('Pet Food'),
            'attributes': {'count': '28 sticks', 'benefit': 'Dental care', 'size': 'Medium'}})
        self._make({'name': 'Interactive Cat Feather Wand', 'sku': 'PET-FEATHERWAND', 'price': 9.99, 'stock': 300,
            'description': 'Extendable 65cm wand, replaceable feather attachment.',
            'image': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400&q=80',
            'category': p, 'brand': self._brand('Pedigree'), 'product_type': self._pt('Pet Toy'),
            'attributes': {'length': '65cm', 'material': 'Feather + Plastic', 'for': 'Cats'}})
        self._make({'name': 'Dog Rope Chew Toy Set 3-pack', 'sku': 'PET-ROPETOY3', 'price': 14.99, 'stock': 250,
            'description': 'Natural cotton rope, 3 sizes, cleans teeth while playing.',
            'image': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&q=80',
            'category': p, 'brand': self._brand('Pedigree'), 'product_type': self._pt('Pet Toy'),
            'attributes': {'count': '3 pieces', 'material': 'Natural Cotton', 'for': 'Dogs'}})
        self._make({'name': 'Pet Grooming Brush Deshedding', 'sku': 'PET-GROOMBRUSH', 'price': 19.99, 'stock': 180,
            'description': 'Stainless steel teeth, ergonomic handle, all coat types.',
            'image': 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=400&q=80',
            'category': p, 'brand': self._brand('Pedigree'), 'product_type': self._pt('Pet Care'),
            'attributes': {'teeth': 'Stainless Steel', 'handle': 'Ergonomic', 'coat': 'All types'}})
        self._make({'name': 'Pedigree Puppy Wet Food 12-pack', 'sku': 'PEDIGREE-PUP12', 'price': 15.99, 'stock': 300,
            'description': 'Chicken in gravy, 12 x 100g pouches, for puppies.',
            'image': 'https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=400&q=80',
            'category': p, 'brand': self._brand('Pedigree'), 'product_type': self._pt('Pet Food'),
            'attributes': {'count': '12 x 100g', 'flavor': 'Chicken in Gravy', 'life_stage': 'Puppy'}})
