from optparse import make_option

from django.core.management.base import BaseCommand

from migrate_dhcp.iscpy.parse import migrate


class Command(BaseCommand):
    args = ''
    option_list = BaseCommand.option_list + (
        make_option('--site-name',
            dest='site_name',
            help='The site name'),
        ) + (
        make_option('--vlan-name',
            dest='vlan_name',
            help='The vlan name'),
        ) + (
        make_option('--vlan-number',
            dest='vlan_number',
            help='The vlan number'),
        ) + (
        make_option('--file-name',
            dest='fname',
            help='The path to the file being imported'),
        ) + (
        make_option('--default-domain',
            dest='default_domain',
            default=None,
            help='Default domain (Watch the output!)'),
        )

    def handle(self, *args, **options):
        migrate(options)
