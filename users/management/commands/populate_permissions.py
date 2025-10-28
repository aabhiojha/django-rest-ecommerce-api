from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Role, Permission, PermissionCategory

class Command(BaseCommand):
    """
    A Django management command to set up the initial roles and permissions
    for the e-commerce application based on a predefined structure.
    """
    help = "Creates default roles (Admin, Seller, Customer) and their associated permissions."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting role and permission setup..."))

        # Clear existing data to ensure a clean slate
        Role.objects.all().delete()
        Permission.objects.all().delete()
        PermissionCategory.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared existing roles, permissions, and categories."))

        # --- Define the structure of permissions ---
        permissions_structure = {
            "User Management": [
                {"name": "View All Users", "code_name": "can_view_users"},
                {"name": "Edit Any User", "code_name": "can_edit_users"},
            ],
            "Product Management": [
                {"name": "Create Products", "code_name": "can_create_products"},
                {"name": "Edit Own Products", "code_name": "can_edit_own_products"},
                {"name": "Delete Own Products", "code_name": "can_delete_own_products"},
                {"name": "Manage All Products", "code_name": "can_manage_all_products"},
                {"name": "Manage Categories", "code_name": "can_manage_categories"},
            ],
            "Order Management": [
                {"name": "View Own Orders", "code_name": "can_view_own_orders"},
                {"name": "Cancel Own Orders", "code_name": "can_cancel_own_orders"},
                {"name": "View Sales Orders (for own products)", "code_name": "can_view_sales_orders"},
                {"name": "Update Order Status", "code_name": "can_update_order_status"},
                {"name": "Manage All Orders", "code_name": "can_manage_all_orders"},
            ],
            "Store Analytics": [
                {"name": "View Seller Dashboard", "code_name": "can_view_seller_dashboard"},
                {"name": "View Admin Dashboard", "code_name": "can_view_admin_dashboard"},
            ],
            "Access Control": [
                {"name": "Manage Roles & Permissions", "code_name": "can_manage_roles"},
                {"name": "Assign Roles to Users", "code_name": "can_assign_roles"},
            ],
        }

        # --- Create Permissions and Categories ---
        all_permissions = []
        for cat_name, perms in permissions_structure.items():
            category, _ = PermissionCategory.objects.get_or_create(name=cat_name)
            self.stdout.write(f"  Created/found category: {category.name}")
            for perm_data in perms:
                permission = Permission.objects.create(
                    category=category,
                    name=perm_data["name"],
                    code_name=perm_data["code_name"],
                )
                all_permissions.append(permission)
                self.stdout.write(f"    - Created permission: {permission.code_name}")

        # --- Create Roles and Assign Permissions ---
        
        # 1. Admin Role (gets all permissions)
        admin_role = Role.objects.create(
            name="Admin",
            slug="admin",
            description="Site administrator with full access.",
            is_system_role=True
        )
        admin_role.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS("\nCreated 'Admin' role with all permissions."))

        # 2. Seller Role
        seller_permissions = Permission.objects.filter(
            code_name__in=[
                "can_create_products",
                "can_edit_own_products",
                "can_delete_own_products",
                "can_view_sales_orders",
                "can_update_order_status",
                "can_view_seller_dashboard",
            ]
        )
        seller_role = Role.objects.create(
            name="Seller",
            slug="seller",
            description="User who can list and manage their own products.",
            is_system_role=True
        )
        seller_role.permissions.set(seller_permissions)
        self.stdout.write(self.style.SUCCESS("Created 'Seller' role with specific product and order permissions."))

        # 3. Customer Role
        customer_permissions = Permission.objects.filter(
            code_name__in=["can_view_own_orders", "can_cancel_own_orders"]
        )
        customer_role = Role.objects.create(
            name="Customer",
            slug="customer",
            description="Default role for a registered user who can make purchases.",
            is_system_role=True
        )
        customer_role.permissions.set(customer_permissions)
        self.stdout.write(self.style.SUCCESS("Created 'Customer' role with basic order management permissions."))

        self.stdout.write(self.style.SUCCESS("\nRole and permission setup complete!"))