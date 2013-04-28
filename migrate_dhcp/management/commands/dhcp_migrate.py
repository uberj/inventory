from django.core.management.base import BaseCommand

from migrate_dhcp.utils import migrate_all


class Command(BaseCommand):
    def handle(self, *args, **options):
        migrate_all()
