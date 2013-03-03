from django.core.management.base import BaseCommand

from migrate_dhcp.utils import do_migrate


class Command(BaseCommand):
    args = ''
    def handle(self, *args, **options):
        if len(args) != 1:
            print "Provide one scope name please."
            return
        do_migrate(args[0])
