from django.core.management.base import BaseCommand

from migrate_dhcp.iscpy.parse import migrate


class Command(BaseCommand):
    args = ''
    def handle(self, *args, **options):
        if len(args) != 4:
            print "Provide site-name vlan-name vlan-number and file-name"
            return
        migrate(args)
