import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from products.models import Category, Product, ProductVarient, ProductImage
from users.models import User


class Command(BaseCommand):
    help = 'Populates the database with sample product data including categories, products, variants, and images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing product data before populating',
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=10,
            help='Number of categories to create (default: 10)',
        )
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Number of products to create (default: 50)',
        )

    def handle(self, *args, **options):
        clear_data = options['clear']
        num_categories = options['categories']
        num_products = options['products']

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing product data...'))
            ProductImage.objects.all().delete()
            ProductVarient.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing data'))

        # Get or create a default user for products
        user = self._get_or_create_default_user()

        # Create categories
        self.stdout.write('Creating categories...')
        categories = self._create_categories(num_categories)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories)} categories'))

        # Create products
        self.stdout.write('Creating products...')
        products = self._create_products(num_products, categories, user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(products)} products'))

        # Create product variants
        self.stdout.write('Creating product variants...')
        variants_count = self._create_product_variants(products)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {variants_count} product variants'))

        # Create product images
        self.stdout.write('Creating product images...')
        images_count = self._create_product_images(products)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {images_count} product images'))

        self.stdout.write(self.style.SUCCESS('\n✅ Successfully populated product data!'))

    def _get_or_create_default_user(self):
        """Get or create a default user for products"""
        user, created = User.objects.get_or_create(
            email='seller@example.com',
            defaults={
                'first_name': 'Default',
                'last_name': 'Seller',
                'is_staff': True,
                'is_active': True,
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created default seller user'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Using existing seller user'))
        return user

    def _create_categories(self, num_categories):
        """Create sample categories with parent-child relationships"""
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Smartphones', 'description': 'Mobile phones and accessories', 'parent': 'Electronics'},
            {'name': 'Laptops', 'description': 'Laptop computers and accessories', 'parent': 'Electronics'},
            {'name': 'Headphones', 'description': 'Audio devices', 'parent': 'Electronics'},
            {'name': 'Clothing', 'description': 'Apparel and fashion'},
            {'name': 'Men\'s Clothing', 'description': 'Clothing for men', 'parent': 'Clothing'},
            {'name': 'Women\'s Clothing', 'description': 'Clothing for women', 'parent': 'Clothing'},
            {'name': 'Home & Kitchen', 'description': 'Home appliances and kitchenware'},
            {'name': 'Furniture', 'description': 'Home and office furniture', 'parent': 'Home & Kitchen'},
            {'name': 'Books', 'description': 'Books and literature'},
            {'name': 'Sports & Outdoors', 'description': 'Sports equipment and outdoor gear'},
            {'name': 'Toys & Games', 'description': 'Toys and games for all ages'},
            {'name': 'Beauty & Personal Care', 'description': 'Beauty products and personal care items'},
            {'name': 'Automotive', 'description': 'Car accessories and parts'},
            {'name': 'Health & Wellness', 'description': 'Health and wellness products'},
        ]

        categories = {}
        created_categories = []

        # First pass: Create parent categories
        for idx, cat_data in enumerate(categories_data[:num_categories]):
            if 'parent' not in cat_data:
                category = Category.objects.create(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    sort_order=idx
                )
                categories[cat_data['name']] = category
                created_categories.append(category)

        # Second pass: Create child categories
        for idx, cat_data in enumerate(categories_data[:num_categories]):
            if 'parent' in cat_data and cat_data['parent'] in categories:
                category = Category.objects.create(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    parent=categories[cat_data['parent']],
                    sort_order=idx
                )
                categories[cat_data['name']] = category
                created_categories.append(category)

        return created_categories

    def _create_products(self, num_products, categories, user):
        """Create sample products"""
        products_templates = [
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest Apple smartphone with titanium design',
                'long_description': 'The iPhone 15 Pro features a stunning titanium design, A17 Pro chip, and advanced camera system.',
                'price': Decimal('999.99'),
                'brand': 'Apple',
                'category': 'Smartphones',
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Premium Android smartphone with S Pen',
                'long_description': 'Galaxy S24 Ultra combines powerful performance with innovative AI features and a brilliant display.',
                'price': Decimal('1199.99'),
                'brand': 'Samsung',
                'category': 'Smartphones',
            },
            {
                'name': 'MacBook Pro 16"',
                'description': 'Powerful laptop for professionals',
                'long_description': 'MacBook Pro with M3 Max chip delivers exceptional performance for demanding workflows.',
                'price': Decimal('2499.99'),
                'brand': 'Apple',
                'category': 'Laptops',
            },
            {
                'name': 'Dell XPS 15',
                'description': 'Premium Windows laptop',
                'long_description': 'Dell XPS 15 features stunning InfinityEdge display and powerful Intel processors.',
                'price': Decimal('1799.99'),
                'brand': 'Dell',
                'category': 'Laptops',
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Premium noise cancelling headphones',
                'long_description': 'Industry-leading noise cancellation with exceptional sound quality and comfort.',
                'price': Decimal('399.99'),
                'brand': 'Sony',
                'category': 'Headphones',
            },
            {
                'name': 'Men\'s Cotton T-Shirt',
                'description': 'Comfortable casual t-shirt',
                'long_description': '100% cotton t-shirt perfect for everyday wear.',
                'price': Decimal('19.99'),
                'brand': 'Generic',
                'category': 'Men\'s Clothing',
            },
            {
                'name': 'Women\'s Summer Dress',
                'description': 'Elegant floral summer dress',
                'long_description': 'Beautiful floral print dress perfect for summer occasions.',
                'price': Decimal('49.99'),
                'brand': 'Fashion Co',
                'category': 'Women\'s Clothing',
            },
            {
                'name': 'Office Chair Pro',
                'description': 'Ergonomic office chair',
                'long_description': 'Comfortable ergonomic chair with lumbar support for long work hours.',
                'price': Decimal('299.99'),
                'brand': 'OfficeMax',
                'category': 'Furniture',
            },
            {
                'name': 'Stainless Steel Cookware Set',
                'description': '10-piece cookware set',
                'long_description': 'Professional-grade stainless steel cookware for your kitchen.',
                'price': Decimal('199.99'),
                'brand': 'KitchenPro',
                'category': 'Home & Kitchen',
            },
            {
                'name': 'Fiction Novel - "The Journey"',
                'description': 'Bestselling fiction novel',
                'long_description': 'An epic tale of adventure and self-discovery.',
                'price': Decimal('14.99'),
                'brand': 'Publisher Inc',
                'category': 'Books',
            },
            {
                'name': 'Yoga Mat Premium',
                'description': 'Non-slip exercise mat',
                'long_description': 'Extra thick yoga mat with superior grip and cushioning.',
                'price': Decimal('39.99'),
                'brand': 'FitLife',
                'category': 'Sports & Outdoors',
            },
            {
                'name': 'LEGO Creator Set',
                'description': 'Building blocks set for kids',
                'long_description': 'Creative building set with 500+ pieces for endless fun.',
                'price': Decimal('59.99'),
                'brand': 'LEGO',
                'category': 'Toys & Games',
            },
            {
                'name': 'Face Moisturizer SPF 30',
                'description': 'Daily face cream with sun protection',
                'long_description': 'Hydrating moisturizer with broad spectrum SPF 30 protection.',
                'price': Decimal('24.99'),
                'brand': 'BeautyGlow',
                'category': 'Beauty & Personal Care',
            },
            {
                'name': 'Car Phone Holder',
                'description': 'Universal dashboard mount',
                'long_description': 'Secure phone holder for hands-free navigation.',
                'price': Decimal('15.99'),
                'brand': 'AutoTech',
                'category': 'Automotive',
            },
            {
                'name': 'Vitamin D3 Supplements',
                'description': 'Daily vitamin supplement',
                'long_description': 'High-potency vitamin D3 for bone and immune health.',
                'price': Decimal('12.99'),
                'brand': 'HealthPlus',
                'category': 'Health & Wellness',
            },
        ]

        # Create category name to object mapping
        category_map = {cat.name: cat for cat in categories}

        products = []
        for i in range(num_products):
            template = products_templates[i % len(products_templates)]
            
            # Get category or use random if not found
            category = category_map.get(template['category'])
            if not category:
                category = random.choice(categories)

            # Generate unique SKU
            sku = f"{template['brand'][:3].upper()}-{random.randint(1000, 9999)}-{i}"

            # Add variation to price for different instances
            price_variation = Decimal(random.uniform(-0.1, 0.1))
            adjusted_price = template['price'] * (1 + price_variation)

            product = Product.objects.create(
                name=f"{template['name']}" if i < len(products_templates) else f"{template['name']} - Model {i}",
                user=user,
                category=category,
                description=template['description'],
                long_description=template['long_description'],
                price=round(adjusted_price, 2),
                sku=sku,
                brand=template['brand'],
                quantity=random.randint(10, 500),
                weight=Decimal(random.uniform(0.1, 5.0)),
                dimensions=f"{random.randint(5, 30)}x{random.randint(5, 30)}x{random.randint(2, 15)} cm",
                is_featured=random.choice([True, False]),
                is_digital=random.choice([True, False]) if 'Book' in template['name'] or 'Software' in template['name'] else False,
                additional_info={
                    'color': random.choice(['Black', 'White', 'Silver', 'Blue', 'Red']),
                    'material': random.choice(['Plastic', 'Metal', 'Cotton', 'Wood', 'Glass']),
                    'warranty': f"{random.randint(1, 3)} years",
                }
            )
            products.append(product)

        return products

    def _create_product_variants(self, products):
        """Create product variants for some products"""
        variant_options = {
            'color': ['Black', 'White', 'Silver', 'Blue', 'Red', 'Gold'],
            'size': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
            'storage': ['64GB', '128GB', '256GB', '512GB', '1TB'],
            'memory': ['8GB', '16GB', '32GB', '64GB'],
        }

        variants_count = 0
        # Create variants for about 30% of products
        for product in random.sample(products, k=int(len(products) * 0.3)):
            # Decide which variant type to use
            if 'phone' in product.name.lower() or 'laptop' in product.name.lower():
                variant_type = 'storage'
                options = variant_options['storage'][:3]
            elif 'clothing' in str(product.category).lower() or 'shirt' in product.name.lower() or 'dress' in product.name.lower():
                variant_type = 'size'
                options = variant_options['size'][:4]
            else:
                variant_type = 'color'
                options = variant_options['color'][:3]

            # Create 2-4 variants per product
            for option in options[:random.randint(2, 4)]:
                price_adjustment = Decimal(random.uniform(-0.15, 0.15))
                variant_price = product.price * (1 + price_adjustment)
                
                ProductVarient.objects.create(
                    product=product,
                    name=f"{variant_type.capitalize()}: {option}",
                    sku=f"{product.sku}-{option[:3].upper()}",
                    price=round(variant_price, 2)
                )
                variants_count += 1

        return variants_count

    def _create_product_images(self, products):
        """Create placeholder product images"""
        images_count = 0
        
        for product in products:
            # Create 1-4 images per product
            num_images = random.randint(1, 4)
            
            for i in range(num_images):
                ProductImage.objects.create(
                    product=product,
                    alt_text=f"{product.name} - Image {i+1}",
                    is_primary=(i == 0),  # First image is primary
                    sort_order=i
                    # Note: image field is left empty as we're creating sample data
                    # In production, you would upload actual images
                )
                images_count += 1

        return images_count
