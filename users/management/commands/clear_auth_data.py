from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import UserRole, Role, Permission, PermissionCategory

class Command(BaseCommand):
    """
    A Django management command to clear all data from auth-related tables.
    This includes UserRole, Role, Permission, and PermissionCategory.
    """
    help = "Clears all data from UserRole, Role, Permission, and PermissionCategory tables."

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Do not prompt for confirmation before deleting data.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Handles the execution of the command.
        """
        if not options['no_input']:
            self.stdout.write(self.style.WARNING(
                "This command will permanently delete all data from the following tables:\n"
                "  - UserRole\n"
                "  - Role\n"
                "  - Permission\n"
                "  - PermissionCategory\n"
            ))
            confirmation = input("Are you sure you want to continue? [y/N] ")
            if confirmation.lower() != 'y':
                self.stdout.write(self.style.ERROR("Operation cancelled by user."))
                return

        self.stdout.write("Starting deletion of auth-related data...")

        # The order of deletion is important to avoid foreign key constraint errors.
        # 1. Delete UserRole entries, which link Users and Roles.
        user_roles_deleted, _ = UserRole.objects.all().delete()
        self.stdout.write(f"  - Deleted {user_roles_deleted} UserRole records.")

        # 2. Delete Roles. This will also clear the Role-Permission M2M table.
        roles_deleted, _ = Role.objects.all().delete()
        self.stdout.write(f"  - Deleted {roles_deleted} Role records.")

        # 3. Delete Permissions, which are linked to PermissionCategory.
        permissions_deleted, _ = Permission.objects.all().delete()
        self.stdout.write(f"  - Deleted {permissions_deleted} Permission records.")

        # 4. Finally, delete the PermissionCategory.
        categories_deleted, _ = PermissionCategory.objects.all().delete()
        self.stdout.write(f"  - Deleted {categories_deleted} PermissionCategory records.")

        self.stdout.write(self.style.SUCCESS(
            "\nSuccessfully cleared all specified auth-related table data."
        ))
