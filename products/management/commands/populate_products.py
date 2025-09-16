from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import (
    Category,
    Product,
    ProductVarient,
    ProductImage,
    ProductAttribute,
)
import random
from decimal import Decimal


class Command(BaseCommand):
    help = "Populate the database with sample product data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before populating",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            # ProductAttribute.objects.all().delete()
            ProductImage.objects.all().delete()
            ProductVarient.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Data cleared!"))

        self.stdout.write(self.style.SUCCESS("Creating sample data..."))

        # Create categories
        self.create_categories()

        # Create products
        self.create_products()

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

    def create_products(self):
        """Create sample products"""
        products_data = [
            # Electronics - Smartphones
            {
                "name": "iPhone 15 Pro",
                "description": "Latest Apple iPhone with Pro features",
                "long_description": "The iPhone 15 Pro features a titanium design, A17 Pro chip, and advanced camera system.",
                "price": Decimal("999.99"),
                "sku": "IPH15PRO001",
                "brand": "Apple",
                "category": "Smartphones",
                "is_featured": True,
                "weight": Decimal("0.187"),
                "dimensions": "146.6 x 70.6 x 8.25 mm",
            },
            {
                "name": "Samsung Galaxy S24",
                "description": "Premium Android smartphone",
                "long_description": "Samsung Galaxy S24 with advanced AI features and stunning camera capabilities.",
                "price": Decimal("799.99"),
                "sku": "SGS24001",
                "brand": "Samsung",
                "category": "Smartphones",
                "is_featured": True,
                "weight": Decimal("0.168"),
                "dimensions": "147.0 x 70.6 x 7.6 mm",
            },
            {
                "name": "Google Pixel 8",
                "description": "Google's flagship smartphone",
                "long_description": "Google Pixel 8 with pure Android experience and exceptional photography.",
                "price": Decimal("699.99"),
                "sku": "GP8001",
                "brand": "Google",
                "category": "Smartphones",
                "weight": Decimal("0.187"),
                "dimensions": "150.5 x 70.8 x 8.9 mm",
            },
            # Electronics - Laptops
            {
                "name": 'MacBook Pro 16"',
                "description": "Professional laptop for creators",
                "long_description": "MacBook Pro 16-inch with M3 Pro chip, perfect for professional work.",
                "price": Decimal("2499.99"),
                "sku": "MBP16M3001",
                "brand": "Apple",
                "category": "Laptops",
                "is_featured": True,
                "weight": Decimal("2.15"),
                "dimensions": "355.7 x 248.1 x 16.8 mm",
            },
            {
                "name": "Dell XPS 13",
                "description": "Ultra-portable Windows laptop",
                "long_description": "Dell XPS 13 with Intel Core i7 and stunning InfinityEdge display.",
                "price": Decimal("1299.99"),
                "sku": "DXPS13001",
                "brand": "Dell",
                "category": "Laptops",
                "weight": Decimal("1.23"),
                "dimensions": "295.7 x 199.04 x 15.8 mm",
            },
            # Electronics - Audio
            {
                "name": "AirPods Pro 2",
                "description": "Premium wireless earbuds",
                "long_description": "AirPods Pro 2nd generation with active noise cancellation.",
                "price": Decimal("249.99"),
                "sku": "APP2001",
                "brand": "Apple",
                "category": "Audio",
                "is_featured": True,
                "weight": Decimal("0.056"),
                "dimensions": "30.9 x 21.8 x 24.0 mm",
            },
            {
                "name": "Sony WH-1000XM5",
                "description": "Premium noise-canceling headphones",
                "long_description": "Sony WH-1000XM5 with industry-leading noise cancellation.",
                "price": Decimal("399.99"),
                "sku": "SWH1000XM5",
                "brand": "Sony",
                "category": "Audio",
                "weight": Decimal("0.249"),
                "dimensions": "254 x 192 x 80 mm",
            },
            # Clothing
            {
                "name": "Nike Air Max 270",
                "description": "Comfortable running shoes",
                "long_description": "Nike Air Max 270 with revolutionary Air cushioning technology.",
                "price": Decimal("130.00"),
                "sku": "NAM270001",
                "brand": "Nike",
                "category": "Shoes",
                "is_featured": True,
                "weight": Decimal("0.31"),
            },
            {
                "name": "Levi's 501 Jeans",
                "description": "Classic straight-leg jeans",
                "long_description": "The original Levi's 501 jeans, a timeless classic.",
                "price": Decimal("69.99"),
                "sku": "L501001",
                "brand": "Levi's",
                "category": "Men's Clothing",
                "weight": Decimal("0.65"),
            },
            # Home & Garden
            {
                "name": "IKEA MALM Bed Frame",
                "description": "Modern wooden bed frame",
                "long_description": "IKEA MALM bed frame in white oak veneer, queen size.",
                "price": Decimal("179.00"),
                "sku": "IKMALM001",
                "brand": "IKEA",
                "category": "Furniture",
                "weight": Decimal("35.5"),
                "dimensions": "209 x 166 x 97 cm",
            },
            # Books
            {
                "name": "The Great Gatsby",
                "description": "Classic American novel",
                "long_description": "F. Scott Fitzgerald's masterpiece about the Jazz Age.",
                "price": Decimal("12.99"),
                "sku": "TGG001",
                "brand": "Scribner",
                "category": "Fiction",
                "is_digital": True,
                "weight": Decimal("0.2"),
            },
        ]

        for product_data in products_data:
            try:
                category = Category.objects.get(name=product_data["category"])
                product = Product.objects.create(
                    name=product_data["name"],
                    slug=slugify(product_data["name"]),
                    description=product_data["description"],
                    long_description=product_data.get("long_description", ""),
                    price=product_data["price"],
                    sku=product_data["sku"],
                    brand=product_data.get("brand", ""),
                    category=category,
                    is_featured=product_data.get("is_featured", False),
                    is_digital=product_data.get("is_digital", False),
                    weight=product_data.get("weight"),
                    dimensions=product_data.get("dimensions", ""),
                )
                self.stdout.write(f"Created product: {product.name}")
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Category "{product_data["category"]}" not found')
                )

    def create_product_variants(self):
        """Create product variants"""
        smartphones = Product.objects.filter(category__name="Smartphones")
        clothing = Product.objects.filter(
            category__name__in=["Shoes", "Men's Clothing"]
        )

        # Create smartphone variants (storage options)
        for phone in smartphones:
            storage_options = ["128GB", "256GB", "512GB"]
            for i, storage in enumerate(storage_options):
                price_increase = Decimal(str(i * 100))  # Convert to string first
                ProductVarient.objects.create(
                    product=phone,
                    name=f"{storage} Storage",
                    sku=f"{phone.sku}-{storage}",
                    price=phone.price + price_increase,
                )

        # Create clothing variants (sizes)
        for item in clothing:
            if item.category.name == "Shoes":
                sizes = ["8", "9", "10", "11", "12"]
            else:
                sizes = ["S", "M", "L", "XL", "XXL"]

            for size in sizes:
                ProductVarient.objects.create(
                    product=item,
                    name=f"Size {size}",
                    sku=f"{item.sku}-{size}",
                    price=item.price,
                )

        self.stdout.write("Created product variants")

    def create_product_attributes(self):
        """Create product attributes"""
        products = Product.objects.all()

        attribute_data = {
            "Electronics": [
                ("Color", ["Black", "White", "Silver", "Gold", "Blue"]),
                ("Warranty", ["1 Year", "2 Years"]),
                ("Connectivity", ["WiFi", "Bluetooth", "5G", "USB-C"]),
            ],
            "Clothing": [
                ("Material", ["Cotton", "Polyester", "Leather", "Denim"]),
                ("Color", ["Black", "White", "Blue", "Red", "Green"]),
                ("Care Instructions", ["Machine Wash", "Hand Wash", "Dry Clean"]),
            ],
            "Home & Garden": [
                ("Material", ["Wood", "Metal", "Plastic", "Glass"]),
                ("Color", ["White", "Black", "Brown", "Natural"]),
                ("Assembly Required", ["Yes", "No"]),
            ],
            "Books": [
                ("Format", ["Paperback", "Hardcover", "E-book"]),
                ("Language", ["English", "Spanish", "French"]),
                ("Pages", ["200-300", "300-400", "400+"]),
            ],
        }

        for product in products:
            parent_category = product.category.parent or product.category
            category_attributes = attribute_data.get(parent_category.name, [])

            # for attr_name, attr_values in category_attributes:
            #     value = random.choice(attr_values)
            #     ProductAttribute.objects.create(
            #         product=product, name=attr_name, value=value
            #     )

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
