from django.db.models import Q

from libs.DHCPHelper import DHCPHelper
from mozdns.address_record.models import AddressRecord
from mozdns.ptr.models import PTR
from mozdns.utils import ensure_label_domain, prune_tree
from core.interface.static_intr.models import StaticInterface
from core.interface.bonded_intr.models import BondedInterface
from core.interface.static_intr.models import StaticIntrKeyValue
from core.vlan.models import Vlan
from core.network.models import Network
from core.interface.utils import coerce_to_bonded
from settings import DHCP_CONFIG_OUTPUT_DIRECTORY

from systems.models import System
from mozdns.view.models import View
from copy import deepcopy
from iscpy.iscpy_core.core import *

def calc_files(dhcp_scope):
    ddir = dhcp_scope.split("-")[0]
    output_file = '-'.join(dhcp_scope.split("-")[1:])
    vlan_generated = "{0}/{1}/{2}_generated_hosts.conf".format(
        DHCP_CONFIG_OUTPUT_DIRECTORY, ddir, output_file
    )

    vlan_file = "{0}/{1}/{2}.conf".format(
        DHCP_CONFIG_OUTPUT_DIRECTORY, ddir, output_file
    )
    return vlan_generated, vlan_file


def migrate_vlan_network_range(dhcp_scope):
    vlan_generated, vlan_file = calc_files(dhcp_scope)
    v, created = Vlan.objects.get_or_create(
        number=dhcp_scope.split('-')[1].strip('vlan'), name="I need a name"
    )
    ft = get_truth(dhcp_scope)
    n, created = Network.objects.get_or_create(
        network=ft.dhcp_scope_start,
        ip_type='4',
    )
    if created:
        print "Created vlan: {0}".format(v)
    else:
        print "Using vlan: {0}".format(v)

def migrate_dhcp(dhcp_scope):
    print "=========== Attempting to migrate {0}".format(dhcp_scope)
    migrate_vlan_network_range(dhcp_scope)
    #migrate_hosts(dhcp_scope)

def migrate_hosts(dhcp_scope):
    dh = DHCPHelper()
    found_a, found_ptr, total = 0, 0, 0
    systems = dh.systems_by_scope(dhcp_scope)
    adapters = []

    for host in systems:
        hostname = host['hostname']
        system = host['sysobj']
        adapters.append(dh.adapters_by_system_and_scope(hostname, dhcp_scope))
        x = dh.adapters_by_system_and_scope(hostname, dhcp_scope)
        for adapter in x:
            total += 1
            # Use dhcp_hostname
            if not adapter:
                print "skipping {0}".format(system)
                continue
            ip = adapter.get('ipv4_address', None)
            if not ip:
                print "No IPv4 Address. skipping {0}".format(system)
                continue
            try:
                a = AddressRecord.objects.get(fqdn=hostname, ip_str=ip)
                found_a +=1
            except AddressRecord.DoesNotExist:
                a = None
            try:
                ptr = PTR.objects.get(name=hostname, ip_str=ip)
                found_ptr  +=1
            except PTR.DoesNotExist:
                ptr = None

            if not a:
                print "Couldn't find A for {0}, {1}".format(hostname, ip)
                continue
            if not ptr:
                print "Couldn't find PTR for {0}, {1}".format(ip, hostname)
                continue
            if a and ptr:
                print "Found matches for {0}".format(system)
            migrate_interface(system, adapter, a, ptr, dhcp_scope)
    print "Total: {0}\nA: {1}\nPTR {2}".format(total, found_a, found_ptr)

def migrate_host(hostname, ip_str, mac, nic_name, options):
    system, created = System.objects.get_or_create(hostname=hostname)
    if created:
        print "Couldn't find a system with hostname {0}"
        print "Creating system..."
        print "System at: {0}".format(system.absolute_url())
    try:
        a = AddressRecord.objects.get(fqdn=hostname, ip_str=ip_str)
    except AddressRecord.DoesNotExist:
        print "Couldn't find A for {0}, {1}".format(hostname, ip_str)
        a = None
    try:
        ptr = PTR.objects.get(name=hostname, ip_str=ip_str)
    except PTR.DoesNotExist:
        print "Couldn't find PTR for {0}, {1}".format(ip_str, hostname)
        ptr = None

    if a and ptr:
        print "Found matches for {0}".format(system)

    intr = migrate_interface(system, a, ptr, ip_str, mac, nic_name, hostname)

    for o in options:
        try:
            kv = StaticIntrKeyValue(key=o[1], value=o[2], obj=intr)
            kv.clean(check_unique=False)
            kv = StaticIntrKeyValue.objects.get(key=o[1], value=o[2], obj=intr)
        except StaticIntrKeyValue.DoesNotExist:
            kv = StaticIntrKeyValue(key=o[1], value=o[2], obj=intr)
            kv.clean()
            kv.save()
    return intr


CREATE_MISSING_A = True
CREATE_MISSING_PTR = True



def migrate_interface(system, a, ptr, ip_str, mac, nic_name, fqdn):
    """
    Migrate a single nic. This function only worries about the A, PTR, and INTR
    objects. Other things take care of KV store options.
    :param system: The system the nic is associated to
    :type system: :class:`System`:
    :param a: The A record this INTR is displacing
    :param ptr: The PTR record this INTR is displacing
    :param mac: The MAC address of the new INTR
    :param fqdn: The fqdn of the interface (usually the same as a.fqdn and
        ptr.name)
    """
    interface_name = nic_name.replace('nic', 'eth')
    if a and ptr and set(a.views.all()) != set(ptr.views.all()):
        import pdb;pdb.set_trace()
        # Shit
        pass
    else:
        if a:
            views = a.views.all()
        elif ptr:
            views = ptr.views.all()
        else:
            views = [View.objects.get(name='private')]

    views = map(deepcopy, [v for v in views])

    # Here lyes the meat of the migration.

    create_a, create_ptr = False, False
    if not ptr and CREATE_MISSING_PTR:
        create_ptr = True
        backup_ptr = None
    else:
        backup_ptr = deepcopy(ptr)
        backup_ptr.id = None

    if not a and CREATE_MISSING_A:
        create_a = True
        backup_a = None
    else:
        backup_a = deepcopy(a)
        backup_a.id = None

    if not (create_ptr or ptr) and not (create_a or a):
        msg = "Failed to resolve handling {0}.".format(system)
        raise Exception(msg)

    print "Going to migrate {0}".format(system)
    if a:
        a.delete(check_cname=False)
    if ptr:
        ptr.delete()
    # i_n = interface_name
    # The cases:
    # 1) There is no SI with this ip, fqdn
    #   * Create new SI
    # 2) There is an SI with this ip, fqdn, i_n and mac
    #   * Already migrated
    # 3) There is an SI with this ip, fqdn, i_n but different mac
    #   * Do bonding logic
    # 4) There is an SI with this ip, fqdn, but different i_n/mac
    #   * Do bonding logic
    # Bonding Logic (a SI 'intr' has already been created):
    #   There is a BI with this mac, i_in
    #       * Migration has already happened
    #   There is a BI with this mac, different i_in
    #       * There is probably a typo in the config, assume migration has
    #       already happened
    #   There is no BI with this mac
    #       * If bonded nics exist, create a new bonded nic
    #       * No bonded nics exist, call coerce on intr

    kwargs = {
        'ip_str': ip_str,
        'ip_type': '4',
        'fqdn': fqdn
    }
    # 1) There is no SI with this ip, fqdn
    #   * Create new SI
    try:
        if not StaticInterface.objects.filter(**kwargs).exists():
            print "Creating new Interface"
            domain = None
            try:
                label, domain = ensure_label_domain(fqdn)
                kwargs['label'], kwargs['domain'] = label, domain
                kwargs['system'] = system
                kwargs['mac'] = mac
                kwargs['interface_name'] = interface_name
                intr = StaticInterface(**kwargs)
                intr.full_clean()
                intr.save()
                for view in views:
                    intr.views.add(view)
            except:
                prune_tree(domain)
                raise
            return intr
        elif StaticInterface.objects.filter(mac=mac, **kwargs).exists():
    # 2) There is an SI with this ip, fqdn, i_n and mac
    #   * Already migrated
            print "Interface already migrated"
            return StaticInterface.objects.get(mac=mac, **kwargs)

    # 3) There is an SI with this ip, fqdn, i_n but different mac
    #   * Do bonding logic
    # 4) There is an SI with this ip, fqdn, but different i_n/mac
    #   * Do bonding logic
        if StaticInterface.objects.filter(~Q(mac=mac), **kwargs).exists():
            intr = StaticInterface.objects.get(~Q(mac=mac), **kwargs)
            do_bonding(intr, mac, interface_name)
    except:
        if backup_a:
            backup_a.save()
        if backup_ptr:
            backup_ptr.save()
        raise
    return intr

# Bonding Logic (a SI 'intr' has already been created):
def do_bonding(intr, mac, interface_name):
    bis = intr.bondedintr_set.all()
#   There is a BI with this mac, i_in
#       * Migration has already happened
    if bis.filter(mac=mac, interface_name=interface_name).exists():
        print "Bonded nic already exists"
        bi = bis.objects.get(mac=mac, interface_name=interface_name)

#   There is a BI with this mac, different i_in
#       * There is probably a typo in the config, assume migration has
#       already happened
    elif bis.filter(~Q(interface_name=interface_name), mac=mac).exists():
        print "!!! Possible typo in the config"
        bi = bis.objects.get(~Q(interface_name=interface_name), mac=mac)

#   There is no BI with this mac
#       * If bonded nics exist, create a new bonded nic
#       * No bonded nics exist, call coerce on intr
    elif not bis.exists():
        print "Coercing {0} to bonded".format(intr)
        intr, bi1 = coerce_to_bonded(intr)
        print "Creating new BI for {0} {1}".format(mac, interface_name)
        bi, _ = BondedInterface.objects.get_or_create(
            mac=mac, interface_name=interface_name, intr=intr
        )
    else:
        bi, _ = BondedInterface.objects.get_or_create(
            mac=intr.mac, interface_name=interface_name, intr=intr
        )
        print "Bonded nic: ".format(bi)
    return intr, bi


def do_migrate(scope):
    migrate_dhcp(scope)
