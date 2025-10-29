from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User, UserRole

class Command(BaseCommand):
    """
    A Django management command to permanently delete all users, their profiles,
    and their role assignments from the database.
    """
    help = "Deletes all users, their profiles, and role assignments."

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
                "This command will permanently delete ALL users, their profiles, and role assignments.\n"
                "Other related data (like Orders or Carts) might be affected depending on your database setup."
            ))
            confirmation = input("Are you sure you want to continue? [y/N] ")
            if confirmation.lower() != 'y':
                self.stdout.write(self.style.ERROR("Operation cancelled by user."))
                return

        self.stdout.write("Starting deletion of all user-related data...")

        # 1. Delete UserRole assignments first to break the link between Users and Roles.
        user_roles_deleted, _ = UserRole.objects.all().delete()
        self.stdout.write(f"  - Deleted {user_roles_deleted} UserRole records.")

        # 2. Delete all User objects.
        # This will also automatically delete the associated UserProfile records
        # because of the on_delete=models.CASCADE setting on the OneToOneField.
        users_deleted, _ = User.objects.all().delete()
        self.stdout.write(f"  - Deleted {users_deleted} User records (and their associated profiles).")

        self.stdout.write(self.style.SUCCESS(
            "\nSuccessfully cleared all user data. The database is ready for fresh user accounts."
        ))