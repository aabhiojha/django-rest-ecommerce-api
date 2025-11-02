from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Role, Permission, PermissionCategory

class Command(BaseCommand):
    """
    A Django management command to set up the initial roles and permissions
    for the e-commerce application based on a predefined structure.
    """
    help = "Creates default roles (Admin, Seller, Customer) and their associated permissions."


    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing roles and permissions before creating new ones',
        )
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Skip creation if roles already exist',
        )


    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting role and permission setup..."))

        try:
            # Check if roles already exist
            if options['skip_if_exists'] and Role.objects.exists():
                self.stdout.write(self.style.WARNING("Roles already exist. Skipping creation."))
                return

            # Clear existing data if --clear flag is provided
            if options['clear']:
                Role.objects.all().delete()
                Permission.objects.all().delete()
                PermissionCategory.objects.all().delete()
                self.stdout.write(self.style.WARNING("Cleared existing roles, permissions, and categories."))

            # --- Define the structure of permissions ---
            permissions_structure = {
            "User Management": [
                # admin
                {"name": "View All Users", "code_name": "can_view_users"},
                {"name": "Edit Any User", "code_name": "can_edit_users"},
                {"name": "Delete Users", "code_name": "can_delete_users"},
                {"name": "Ban/Suspend Users", "code_name": "can_ban_users"},
            ],
            "Product Management": [
                # seller
                {"name": "View Own Products", "code_name": "can_view_own_products"},
                {"name": "Create Products", "code_name": "can_create_products"},
                {"name": "Edit Own Products", "code_name": "can_edit_own_products"},
                {"name": "Delete Own Products", "code_name": "can_delete_own_products"},
                # admin
                {"name": "Manage All Products", "code_name": "can_manage_all_products"},
                {"name": "Manage Categories", "code_name": "can_manage_categories"},
            ],
            "Order Management": [
                # customer
                {"name": "Place Orders", "code_name": "can_place_orders"},
                {"name": "View Own Orders", "code_name": "can_view_own_orders"},
                {"name": "Cancel Own Orders", "code_name": "can_cancel_own_orders"},
                # seller
                {"name": "View Sales Orders (for own products)", "code_name": "can_view_sales_orders"},
                {"name": "Update Order Status", "code_name": "can_update_order_status"},
                # Admin
                {"name": "Manage All Orders", "code_name": "can_manage_all_orders"},
                {"name": "Override Order Status", "code_name": "can_override_order_status"},
            ],
            "Store Analytics": [
                # Seller
                {"name": "View Seller Dashboard", "code_name": "can_view_seller_dashboard"},
                # Admin
                {"name": "View Admin Dashboard", "code_name": "can_view_admin_dashboard"},
            ],
            "Access Control": [
                # admin
                {"name": "Manage Roles & Permissions", "code_name": "can_manage_roles"},
                {"name": "Assign Roles to Users", "code_name": "can_assign_roles"},
            ],
            "Review Management": [
                # Customer
                {"name": "Create Review", "code_name": "can_create_review"},
                {"name": "Delete own review", "code_name": "can_delete_own_review"},
                {"name": "Edit own review", "code_name": "can_edit_own_review"},
                # seller
                {"name": "Reply to review", "code_name":"can_reply_own_product_review"},
                # Admin
                {"name": "Reply to all review", "code_name":"can_reply_all_review"},
                {"name": "Delete all review", "code_name":"can_delete_all_review"},
            ],
        }

            # --- Create Permissions and Categories ---
            all_permissions = []
            for cat_name, perms in permissions_structure.items():
                category, created = PermissionCategory.objects.get_or_create(name=cat_name)
                status = "Created" if created else "Found"
                self.stdout.write(f"  {status} category: {category.name}")
                
                for perm_data in perms:
                    permission, created = Permission.objects.get_or_create(
                        code_name=perm_data["code_name"],
                        defaults={
                            "category": category,
                            "name": perm_data["name"],
                        }
                    )
                    all_permissions.append(permission)
                    status = "Created" if created else "Found"
                    self.stdout.write(f"    - {status} permission: {permission.code_name}")

            # Verify all permissions were created
            expected_count = sum(len(perms) for perms in permissions_structure.values())
            actual_count = len(all_permissions)
            if expected_count != actual_count:
                self.stdout.write(
                    self.style.WARNING(
                        f"Warning: Expected {expected_count} permissions but got {actual_count}"
                    )
                )

            # --- Create Roles and Assign Permissions ---
            
            # 1. Admin Role (gets all permissions)
            admin_role, created = Role.objects.get_or_create(
                slug="admin",
                defaults={
                    "name": "Admin",
                    "description": "Site administrator with full access.",
                    "is_system_role": True
                }
            )
            admin_role.permissions.set(all_permissions)
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"\n{status} 'Admin' role with all permissions."))

            # 2. Seller Role
            seller_permissions = Permission.objects.filter(
                code_name__in=[
                    "can_view_own_products", 
                    "can_create_products",
                    "can_edit_own_products",
                    "can_delete_own_products",
                    "can_view_sales_orders",
                    "can_update_order_status",
                    "can_view_seller_dashboard",
                    "can_reply_own_product_review",
                ]
            )
            seller_role, created = Role.objects.get_or_create(
                slug="seller",
                defaults={
                    "name": "Seller",
                    "description": "User who can list and manage their own products.",
                    "is_system_role": True
                }
            )
            seller_role.permissions.set(seller_permissions)
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{status} 'Seller' role with {seller_permissions.count()} permissions."))

            # 3. Customer Role
            customer_permissions = Permission.objects.filter(
                code_name__in=[
                    "can_place_orders", 
                    "can_view_own_orders",
                    "can_cancel_own_orders",
                    "can_create_review", 
                    "can_delete_own_review",
                    "can_edit_own_review", 
                ]
            )
            customer_role, created = Role.objects.get_or_create(
                slug="customer",
                defaults={
                    "name": "Customer",
                    "description": "Default role for a registered user who can make purchases.",
                    "is_system_role": True
                }
            )
            customer_role.permissions.set(customer_permissions)
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{status} 'Customer' role with {customer_permissions.count()} permissions."))

            # Verify role creation
            self._verify_roles()
            
            # Print summary
            self._print_summary()
            
            self.stdout.write(self.style.SUCCESS("\n✅ Role and permission setup complete!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error during setup: {str(e)}"))
            raise

    def _verify_roles(self):
        """Verify that roles have the correct number of permissions."""
        admin_role = Role.objects.get(slug="admin")
        seller_role = Role.objects.get(slug="seller")
        customer_role = Role.objects.get(slug="customer")
        
        self.stdout.write("\n--- Verification ---")
        self.stdout.write(f"Admin permissions: {admin_role.permissions.count()}")
        self.stdout.write(f"Seller permissions: {seller_role.permissions.count()}")
        self.stdout.write(f"Customer permissions: {customer_role.permissions.count()}")

    def _print_summary(self):
        """Print a summary of created roles and permissions."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("SETUP SUMMARY"))
        self.stdout.write("="*50)
        
        total_categories = PermissionCategory.objects.count()
        total_permissions = Permission.objects.count()
        total_roles = Role.objects.count()
        
        self.stdout.write(f"📁 Categories created: {total_categories}")
        self.stdout.write(f"🔐 Permissions created: {total_permissions}")
        self.stdout.write(f"👥 Roles created: {total_roles}\n")
        
        # List each role with permission count
        for role in Role.objects.all().order_by('name'):
            perm_count = role.permissions.count()
            self.stdout.write(
                f"  • {role.name} ({role.slug}): {perm_count} permissions"
            )
        
        self.stdout.write("="*50 + "\n")