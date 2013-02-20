from libs.DHCPHelper import DHCPHelper
from django.test.client import Client
from systems.models import ScheduledTask
from mozdns.address_record.models import AddressRecord
from mozdns.ptr.models import PTR
from mozdns.utils import ensure_label_domain, prune_tree
from core.interface.static_intr.models import StaticInterface
from core.vlan.models import Vlan
from core.network.models import Network
from truth.models import Truth

from copy import deepcopy
import simplejson as json

def get_all_scopes():
    client = Client()
    dhcp_scopes = []
    dhcp_scopes = json.loads(client.get('/api/keyvalue/?key=is_dhcp_scope', follow=True).content)
    #print dhcp_scopes
    for dhcp_scope in dhcp_scopes:
        dhcp_scope = dhcp_scope.split(":")[1]
        ScheduledTask.objects.get_or_create(task=dhcp_scope, type='dhcp')
    dh = DHCPHelper()
    dhcp_scopes = dh.get_scopes_to_generate()
    return dhcp_scopes

def migrate_all():
    for dhcp_scope in get_all_scopes():
        migrate_dhcp(dhcp_scope.task)

def migrate_vlan_network_range(dhcp_scope):
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


CREATE_MISSING_A = True
CREATE_MISSING_PTR = True


class FakeKV(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class FakeScope(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k.replace('.', '_'), v)

def get_truth(dhcp_scope):
    import pdb;pdb.set_trace()
    truth = Truth.objects.get(name=dhcp_scope)
    fs = FakeScope(
        **dict([(kv.key, kv.value) for kv in truth.keyvalue_set.all()])
    )
    return fs


def migrate_interface(system, kvs, a, ptr, dhcp_scope):
    if a and ptr and set(a.views.all()) != set(ptr.views.all()):
        import pdb;pdb.set_trace()
        # Shit
        pass
    else:
        if a:
            views = a.views.all()
        else:
            views = ptr.views.all()

    views = map(deepcopy, [v for v in views])

    oldkv = FakeKV(system=system, dhcp_scope=dhcp_scope, **kvs)

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
        msg = "Failed to resolve handling {0} {1}.".format(system, oldkv)
        raise Exception(msg)

    print "Going to migrate {0} {1}".format(system, oldkv)
    kwargs = {
        'ip_str': oldkv.ipv4_address,
        'ip_type': '4',
        'system': system,
        'mac': oldkv.mac_address,
    }
    if a:
        a.delete(check_cname=False)
    if ptr:
        ptr.delete()
    try:
        try:
            intr = StaticInterface.objects.get(**kwargs)
            print "Interface already created."
        except StaticInterface.DoesNotExist:
            print "Creating new Interface"
            domain = None
            try:
                label, domain = ensure_label_domain(oldkv.system_hostname)
                kwargs['label'], kwargs['domain'] = label, domain
                intr = StaticInterface(**kwargs)
                intr.full_clean()
                intr.save()
                for view in views:
                    intr.views.add(view)
            except:
                prune_tree(domain)
                raise
    except:
        if backup_a:
            backup_a.save()
        if backup_ptr:
            backup_ptr.save()
        raise
    print intr


def do_migrate(scope):
    migrate_dhcp(scope)
