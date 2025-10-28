from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import (
    Category,
    Product,
    ProductVarient,
    ProductImage,
)
import random
from decimal import Decimal
from faker import Faker


class Command(BaseCommand):
    help = "Populate the database with sample product data"

    def __init__(self):
        super().__init__()
        self.faker = Faker()

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before populating",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of products to create (default: 100)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            ProductImage.objects.all().delete()
            ProductVarient.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Data cleared!"))

        self.stdout.write(self.style.SUCCESS("Creating sample data..."))

        # Create categories
        # self.create_categories()

        # Create products
        self.create_products(count=options.get("count", 100))

        # Create product variants
        self.create_product_variants()

        # Create product attributes
        self.create_product_attributes()

        # Create product images
        self.create_product_images()

        self.stdout.write(self.style.SUCCESS("Sample data created successfully!"))

    def create_categories(self):
        """Create sample categories"""
        categories_data = [
            {
                "name": "Electronics",
                "description": "Electronic devices and gadgets",
                "sort_order": 1,
                "children": [
                    {
                        "name": "Smartphones",
                        "description": "Mobile phones and accessories",
                    },
                    {
                        "name": "Laptops",
                        "description": "Laptop computers and accessories",
                    },
                    {
                        "name": "Tablets",
                        "description": "Tablet computers and accessories",
                    },
                    {
                        "name": "Audio",
                        "description": "Headphones, speakers, and audio equipment",
                    },
                ],
            },
            {
                "name": "Clothing",
                "description": "Fashion and apparel",
                "sort_order": 2,
                "children": [
                    {"name": "Men's Clothing", "description": "Clothing for men"},
                    {"name": "Women's Clothing", "description": "Clothing for women"},
                    {"name": "Shoes", "description": "Footwear for all"},
                    {"name": "Accessories", "description": "Fashion accessories"},
                ],
            },
            {
                "name": "Home & Garden",
                "description": "Home improvement and garden supplies",
                "sort_order": 3,
                "children": [
                    {"name": "Furniture", "description": "Home furniture"},
                    {"name": "Kitchen", "description": "Kitchen appliances and tools"},
                    {"name": "Garden", "description": "Gardening tools and supplies"},
                ],
            },
            {
                "name": "Books",
                "description": "Books and educational materials",
                "sort_order": 4,
                "children": [
                    {"name": "Fiction", "description": "Fiction books"},
                    {"name": "Non-Fiction", "description": "Non-fiction books"},
                    {"name": "Textbooks", "description": "Educational textbooks"},
                ],
            },
        ]

        for cat_data in categories_data:
            parent_category = Category.objects.create(
                name=cat_data["name"],
                slug=slugify(cat_data["name"]),
                description=cat_data["description"],
                sort_order=cat_data["sort_order"],
            )
            self.stdout.write(f"Created parent category: {parent_category.name}")

            for child_data in cat_data.get("children", []):
                child_category = Category.objects.create(
                    name=child_data["name"],
                    slug=slugify(child_data["name"]),
                    description=child_data["description"],
                    parent=parent_category,
                    sort_order=0,
                )
                self.stdout.write(f"  Created child category: {child_category.name}")

    def generate_product_name(self, category_name):
        """Generate realistic product names based on category"""
        category_templates = {
            "Smartphones": ["Pro", "Max", "Ultra", "Plus", "Mini", "Lite"],
            "Laptops": ["Pro", "Air", "Book", "Elite", "Spectre", "Pavilion"],
            "Audio": ["Pro", "Studio", "Max", "Buds", "Elite", "Premium"],
            "Shoes": ["Air", "Boost", "Zoom", "Runner", "Sport", "Classic"],
            "Men's Clothing": ["Classic", "Premium", "Essential", "Modern", "Vintage"],
            "Women's Clothing": ["Classic", "Premium", "Essential", "Modern", "Vintage"],
            "Furniture": ["Modern", "Classic", "Deluxe", "Comfort", "Premium"],
            "Fiction": self.faker.catch_phrase(),
            "Non-Fiction": self.faker.catch_phrase(),
        }
        
        brand_prefix = self.faker.company().split()[0]
        template = random.choice(category_templates.get(category_name, ["Series"]))
        
        if "Clothing" in category_name or "Shoes" in category_name:
            return f"{brand_prefix} {template} {random.choice(['Shirt', 'Pants', 'Jacket', 'Dress', 'Sneakers'])} {random.randint(100, 999)}"
        elif "Book" in category_name or category_name in ["Fiction", "Non-Fiction"]:
            return self.faker.catch_phrase()
        else:
            return f"{brand_prefix} {category_name[:-1] if category_name.endswith('s') else category_name} {template} {random.randint(100, 999)}"
    
    def generate_price(self, parent_category):
        """Generate realistic prices based on parent category"""
        price_ranges = {
            "Electronics": (299.99, 2999.99),
            "Clothing": (19.99, 199.99),
            "Home & Garden": (49.99, 999.99),
            "Books": (9.99, 49.99),
        }
        
        min_price, max_price = price_ranges.get(parent_category, (19.99, 199.99))
        price = round(random.uniform(min_price, max_price), 2)
        return Decimal(str(price))

    def create_products(self, count=100):
        """Create sample products dynamically using existing categories"""
        categories = Category.objects.filter(parent__isnull=False)
        
        if not categories.exists():
            self.stdout.write(self.style.ERROR("No child categories found. Please create categories first."))
            return
        
        self.stdout.write(f"Creating {count} products...")
        
        for i in range(count):
            category = random.choice(categories)
            parent_category = category.parent.name if category.parent else category.name
            
            product_name = self.generate_product_name(category.name)
            price = self.generate_price(parent_category)
            
            # Generate SKU
            sku_prefix = ''.join([c for c in product_name if c.isupper()])[:5]
            sku = f"{sku_prefix}{random.randint(1000, 9999)}"
            
            # Make SKU unique
            while Product.objects.filter(sku=sku).exists():
                sku = f"{sku_prefix}{random.randint(1000, 9999)}"
            
            product = Product.objects.create(
                name=product_name,
                slug=slugify(product_name),
                description=self.faker.sentence(nb_words=10),
                long_description=self.faker.paragraph(nb_sentences=5),
                price=price,
                sku=sku,
                brand=self.faker.company(),
                category=category,
                is_featured=random.choice([True, False]) if random.random() < 0.2 else False,
                is_digital=True if parent_category == "Books" else False,
                weight=Decimal(str(round(random.uniform(0.1, 5.0), 2))),
                dimensions=f"{random.randint(100, 400)} x {random.randint(50, 300)} x {random.randint(5, 100)} mm",
            )
            
            if (i + 1) % 20 == 0:
                self.stdout.write(f"Created {i + 1} products...")
        
        self.stdout.write(self.style.SUCCESS(f"Created {count} products successfully!"))

    def create_product_variants(self):
        """Create product variants"""
        products = Product.objects.all()
        
        variant_options = {
            "Electronics": {
                "Storage": ["64GB", "128GB", "256GB", "512GB", "1TB"],
                "Color": ["Black", "White", "Silver", "Gold", "Blue", "Red"],
            },
            "Clothing": {
                "Size": ["XS", "S", "M", "L", "XL", "XXL"],
                "Color": ["Black", "White", "Blue", "Red", "Green", "Grey"],
            },
            "Shoes": {
                "Size": ["7", "8", "9", "10", "11", "12"],
                "Color": ["Black", "White", "Blue", "Red"],
            },
        }

        for product in products:
            parent_category = product.category.parent.name if product.category.parent else product.category.name
            
            # 70% of products get variants
            if random.random() < 0.7:
                category_variants = variant_options.get(parent_category, {})
                
                if category_variants:
                    variant_type = random.choice(list(category_variants.keys()))
                    options = category_variants[variant_type]
                    
                    for i, option in enumerate(random.sample(options, min(3, len(options)))):
                        price_variation = Decimal(str(random.uniform(-10, 50)))
                        ProductVarient.objects.create(
                            product=product,
                            name=f"{variant_type}: {option}",
                            sku=f"{product.sku}-{option.replace(' ', '')}",
                            price=product.price + price_variation,
                        )

        self.stdout.write("Created product variants")

    def create_product_attributes(self):
        """Create product attributes using additional_info JSON field"""
        products = Product.objects.all()

        attribute_data = {
            "Electronics": {
                "Color": ["Black", "White", "Silver", "Gold", "Blue"],
                "Warranty": ["1 Year", "2 Years"],
                "Connectivity": ["WiFi", "Bluetooth", "5G", "USB-C"],
            },
            "Clothing": {
                "Material": ["Cotton", "Polyester", "Leather", "Denim"],
                "Color": ["Black", "White", "Blue", "Red", "Green"],
                "Care Instructions": ["Machine Wash", "Hand Wash", "Dry Clean"],
            },
            "Home & Garden": {
                "Material": ["Wood", "Metal", "Plastic", "Glass"],
                "Color": ["White", "Black", "Brown", "Natural"],
                "Assembly Required": ["Yes", "No"],
            },
            "Books": {
                "Format": ["Paperback", "Hardcover", "E-book"],
                "Language": ["English", "Spanish", "French"],
                "Pages": ["200-300", "300-400", "400+"],
            },
        }

        for product in products:
            parent_category = product.category.parent or product.category
            category_attrs = attribute_data.get(parent_category.name, {})
            
            additional_info = {}
            for attr_name, attr_values in category_attrs.items():
                additional_info[attr_name] = random.choice(attr_values)
            
            if additional_info:
                product.additional_info = additional_info
                product.save()

        self.stdout.write("Created product attributes")

    def create_product_images(self):
        """Create placeholder product images"""
        products = Product.objects.all()

        for product in products:
            # Create 2-4 images per product
            num_images = random.randint(2, 4)

            for i in range(num_images):
                ProductImage.objects.create(
                    product=product,
                    image=f"products/placeholder_{product.id}_{i+1}.jpg",
                    alt_text=f"{product.name} - Image {i+1}",
                    is_primary=(i == 0),  # First image is primary
                    sort_order=i,
                )

        self.stdout.write("Created product images")
