from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from users.models import (
    User,
    UserProfile,
    Address,
    PermissionCategory,
    Permission,
    Role,
    UserRole,
)


class Command(BaseCommand):
    help = "Populate users app with sample data including RBAC permissions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before populating",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            UserRole.objects.all().delete()
            Role.objects.all().delete()
            Permission.objects.all().delete()
            PermissionCategory.objects.all().delete()
            Address.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Data cleared!"))

        try:
            with transaction.atomic():
                # Create Permission Categories
                self.stdout.write("Creating permission categories...")
                categories = self.create_permission_categories()

                # Create Permissions
                self.stdout.write("Creating permissions...")
                permissions = self.create_permissions(categories)

                # Create Roles
                self.stdout.write("Creating roles...")
                roles = self.create_roles(permissions)

                # Create Users
                self.stdout.write("Creating users...")
                users = self.create_users()

                # Assign Roles to Users
                self.stdout.write("Assigning roles to users...")
                self.assign_roles(users, roles)

                # Create User Profiles
                self.stdout.write("Creating user profiles...")
                self.create_user_profiles(users)

                # Create Addresses
                self.stdout.write("Creating addresses...")
                self.create_addresses(users)

                self.stdout.write(
                    self.style.SUCCESS("Successfully populated users app!")
                )
                self.print_summary(users, roles, permissions, categories)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def create_permission_categories(self):
        categories_data = [
            {
                "name": "User Management",
                "slug": "user-management",
                "description": "Permissions related to user management",
            },
            {
                "name": "Product Management",
                "slug": "product-management",
                "description": "Permissions related to product management",
            },
            {
                "name": "Order Management",
                "slug": "order-management",
                "description": "Permissions related to order management",
            },
            {
                "name": "Inventory Management",
                "slug": "inventory-management",
                "description": "Permissions related to inventory management",
            },
            {
                "name": "Content Management",
                "slug": "content-management",
                "description": "Permissions related to content management",
            },
            {
                "name": "Analytics",
                "slug": "analytics",
                "description": "Permissions related to analytics and reports",
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = PermissionCategory.objects.get_or_create(
                slug=cat_data["slug"],
                defaults={
                    "name": cat_data["name"],
                    "description": cat_data["description"],
                },
            )
            categories[cat_data["slug"]] = category
            if created:
                self.stdout.write(f"  Created category: {category.name}")

        return categories

    def create_permissions(self, categories):
        permissions_data = [
            # User Management
            ("View Users", "can_view_users", "user-management"),
            ("Create Users", "can_create_users", "user-management"),
            ("Edit Users", "can_edit_users", "user-management"),
            ("Delete Users", "can_delete_users", "user-management"),
            ("Manage Roles", "can_manage_roles", "user-management"),
            # Product Management
            ("View Products", "can_view_products", "product-management"),
            ("Create Products", "can_create_products", "product-management"),
            ("Edit Products", "can_edit_products", "product-management"),
            ("Delete Products", "can_delete_products", "product-management"),
            ("Manage Categories", "can_manage_categories", "product-management"),
            # Order Management
            ("View Orders", "can_view_orders", "order-management"),
            ("Create Orders", "can_create_orders", "order-management"),
            ("Edit Orders", "can_edit_orders", "order-management"),
            ("Cancel Orders", "can_cancel_orders", "order-management"),
            ("Process Refunds", "can_process_refunds", "order-management"),
            # Inventory Management
            ("View Inventory", "can_view_inventory", "inventory-management"),
            ("Update Stock", "can_update_stock", "inventory-management"),
            ("Transfer Stock", "can_transfer_stock", "inventory-management"),
        ]

        permissions = {}
        for name, code_name, category_slug in permissions_data:
            permission, created = Permission.objects.get_or_create(
                code_name=code_name,
                defaults={
                    "name": name,
                    "category": categories[category_slug],
                    "description": f"Permission to {name.lower()}",
                },
            )
            permissions[code_name] = permission
            if created:
                self.stdout.write(f"  Created permission: {permission.name}")
        return permissions

    def create_roles(self, permissions):
        roles_data = [
            {
                "name": "Super Admin",
                "slug": "super-admin",
                "description": "Full access to all system features",
                "is_system_role": True,
                "permissions": list(permissions.keys()),
            },
            {
                "name": "Store Manager",
                "slug": "store-manager",
                "description": "Manage products, orders, and inventory",
                "is_system_role": True,
                "permissions": [
                    "can_view_products",
                    "can_create_products",
                    "can_edit_products",
                    "can_manage_categories",
                    "can_view_orders",
                    "can_edit_orders",
                    "can_cancel_orders",
                    "can_view_inventory",
                    "can_update_stock",
                    "can_view_reports",
                ],
            },
            {
                "name": "Sales Representative",
                "slug": "sales-representative",
                "description": "Handle customer orders and basic product viewing",
                "is_system_role": False,
                "permissions": [
                    "can_view_products",
                    "can_view_orders",
                    "can_create_orders",
                    "can_edit_orders",
                ],
            },
            {
                "name": "Inventory Manager",
                "slug": "inventory-manager",
                "description": "Manage inventory and stock levels",
                "is_system_role": False,
                "permissions": [
                    "can_view_inventory",
                    "can_update_stock",
                    "can_transfer_stock",
                    "can_view_products",
                ],
            },
            {
                "name": "Customer",
                "slug": "customer",
                "description": "Regular customer with basic access",
                "is_system_role": True,
                "permissions": [
                    "can_view_products",
                    "can_create_orders",
                ],
            },
        ]

        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                slug=role_data["slug"],
                defaults={
                    "name": role_data["name"],
                    "description": role_data["description"],
                    "is_system_role": role_data["is_system_role"],
                },
            )

            # Add permissions
            for perm_code in role_data["permissions"]:
                if perm_code in permissions:
                    role.permissions.add(permissions[perm_code])

            roles[role_data["slug"]] = role
            if created:
                self.stdout.write(f"  Created role: {role.name}")

        return roles

    def create_users(self):
        users_data = [
            {
                "email": "manager@gmail.com",
                "password": "manager",
                "first_name": "Store",
                "last_name": "Manager",
                "phone": "9841234568",
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "email": "sales@gmail.com",
                "password": "sales",
                "first_name": "Sales",
                "last_name": "Rep",
                "phone": "9841234569",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "email": "inventory@gmail.com",
                "password": "inventory",
                "first_name": "Inventory",
                "last_name": "Manager",
                "phone": "9841234570",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "email": "customer1@gmail.com",
                "password": "customer",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "9841234571",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "email": "customer2@gmail.com",
                "password": "customer",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "9841234572",
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "phone": user_data["phone"],
                    "is_staff": user_data["is_staff"],
                    "is_superuser": user_data["is_superuser"],
                },
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(f"  Created User: {user.email}")
            users.append(user)

        return users

    def assign_roles(self, users, roles):
        role_assignments = [
            (0, "super-admin"),  # manager@gmail.com -> Super Admin
            (1, "store-manager"),  # sales@gmail.com -> Store Manager (Fixed)
            (2, "sales-representative"),  # inventory@gmail.com -> Sales Rep (Fixed)
            (3, "inventory-manager"),  # customer1@gmail.com -> Inventory Manager (Fixed)
            (4, "customer"),  # customer2@gmail.com -> Customer (Fixed)
        ]

        # Get first user as assigned_by, or use None if no users exist
        assigned_by = users[0] if users else None

        for user_idx, role_slug in role_assignments:
            if user_idx >= len(users):
                continue
            
            user = users[user_idx]
            role = roles.get(role_slug)
            
            if not role:
                self.stdout.write(self.style.WARNING(f"  Role {role_slug} not found"))
                continue

            user_role, created = UserRole.objects.get_or_create(
                user=user, role=role, defaults={"assigned_by": assigned_by}
            )
            if created:
                self.stdout.write(f"  Assigned {role.name} to {user.email}")

    def create_user_profiles(self, users):
        profiles_data = [
            {
                "bio": "Managing store operations and inventory",
                "gender": "male",
                "location": "Pokhara, Nepal",
            },
            {
                "bio": "Sales representative handling customer orders",
                "gender": "female",
                "location": "Lalitpur, Nepal",
            },
            {
                "bio": "Managing warehouse inventory",
                "gender": "male",
                "location": "Bhaktapur, Nepal",
            },
            {
                "bio": "Regular customer",
                "gender": "male",
                "location": "Kathmandu, Nepal",
            },
            {
                "bio": "Regular customer",
                "gender": "female",
                "location": "Biratnagar, Nepal",
            },
        ]

        for user, profile_data in zip(users, profiles_data):
            profile, created = UserProfile.objects.get_or_create(
                user=user, defaults=profile_data
            )
            if created:
                self.stdout.write(f"  Created profile for {user.email}")

    def create_addresses(self, users):
        addresses_data = [
            # Manager addresses
            [
                {
                    "address_type": "work",
                    "full_name": "Store Manager",
                    "phone": "9841234568",
                    "address_line_1": "Lakeside",
                    "address_line_2": "Hallanchowk",
                    "city": "Pokhara",
                    "state": "gandaki",
                    "is_default": True,
                }
            ],
            # Sales rep addresses
            [
                {
                    "address_type": "home",
                    "full_name": "Sales Rep",
                    "phone": "9841234569",
                    "address_line_1": "Pulchowk",
                    "address_line_2": "",
                    "city": "Lalitpur",
                    "state": "bagmati",
                    "is_default": True,
                }
            ],
            # Inventory manager addresses
            [
                {
                    "address_type": "home",
                    "full_name": "Inventory Manager",
                    "phone": "9841234570",
                    "address_line_1": "Dhulikhel Road",
                    "address_line_2": "",
                    "city": "Bhaktapur",
                    "state": "bagmati",
                    "is_default": True,
                }
            ],
            # John Doe addresses
            [
                {
                    "address_type": "home",
                    "full_name": "John Doe",
                    "phone": "9841234571",
                    "address_line_1": "Baneshwor",
                    "address_line_2": "Near Viber Office",
                    "city": "Kathmandu",
                    "state": "bagmati",
                    "is_default": True,
                },
                {
                    "address_type": "work",
                    "full_name": "John Doe",
                    "phone": "9841234571",
                    "address_line_1": "Durbarmarg",
                    "address_line_2": "",
                    "city": "Kathmandu",
                    "state": "bagmati",
                    "is_default": False,
                },
            ],
            # Jane Smith addresses
            [
                {
                    "address_type": "home",
                    "full_name": "Jane Smith",
                    "phone": "9841234572",
                    "address_line_1": "Traffic Chowk",
                    "address_line_2": "",
                    "city": "Biratnagar",
                    "state": "koshi",
                    "is_default": True,
                }
            ],
        ]

        for user, user_addresses in zip(users, addresses_data):
            for addr_data in user_addresses:
                address, created = Address.objects.get_or_create(
                    user=user,
                    address_line_1=addr_data["address_line_1"],
                    defaults=addr_data,
                )

                if created:
                    self.stdout.write(
                        f"  Created {addr_data['address_type']} address for {user.email}"
                    )

    def print_summary(self, users, roles, permissions, categories):
        self.stdout.write("\n" + "=" * 60)
        # success = hariyo ma dekhaucha
        self.stdout.write(self.style.SUCCESS("POPULATION SUMMARY"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Permission Categories: {len(categories)}")
        self.stdout.write(f"Permissions: {len(permissions)}")
        self.stdout.write(f"Roles: {len(roles)}")
        self.stdout.write(f"Users: {len(users)}")
        # warning = pahelo ma lekhchaa
        self.stdout.write("\n" + self.style.WARNING("TEST CREDENTIALS:"))
        self.stdout.write("-" * 60)
        self.stdout.write("Store Manager    : manager@gmail.com / manager")
        self.stdout.write("Sales Rep        : sales@gmail.com / sales")
        self.stdout.write("Inventory Mgr    : inventory@gmail.com / inventory")
        self.stdout.write("Customer 1       : customer1@gmail.com / customer")
        self.stdout.write("Customer 2       : customer2@gmail.com / customer")
        self.stdout.write("=" * 60 + "\n")