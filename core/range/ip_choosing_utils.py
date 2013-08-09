# First we need to raise the JSON pk's into ORM objects
from django.db.models import Q
from django.shortcuts import get_object_or_404
from core.site.models import Site
from core.vlan.models import Vlan
from core.network.models import Network


def pks_to_objs(pks, Klass):
    return map(lambda pk: get_object_or_404(Klass, pk=pk), pks)


def calculate_filters(choice_type, choice_pk):
    """
    Write three functions that given a list of present primary keys
    ('present_pks') that are in the UI will remove the correct pk's and
    return a list of raised objects.

    filter_network will return a list of Networks
    filter_site will return a list of Sites
    filter_vlan will return a list of Vlans

    The 'present_pks' value is a list of integers that represent primary
    keys of the type of objects the function returns.
    """
    if choice_type == 'network':
        network = get_object_or_404(Network, pk=choice_pk)

        def filter_network(present_pks):
            return [network]

        def filter_site(present_pks):
            return [network.site] if network.site else []

        def filter_vlan(present_pks):
            return [network.vlan] if network.vlan else []

    elif choice_type == 'site':
        def filter_network(present_pks):
            """
            Remove any present network pk's that aren't in the network
            """
            site_network_pks = get_object_or_404(
                Site, pk=choice_pk
            ).network_set.all().values_list('pk', flat=True)
            net_pks = set(present_pks).intersection(set(site_network_pks))
            return pks_to_objs(net_pks, Network)

        def filter_site(present_pks):
            return [get_object_or_404(Site, pk=choice_pk)]

        def filter_vlan(present_pks):
            vlans = pks_to_objs(present_pks, Vlan)

            def is_in_site(vlan):
                return vlan.network_set.filter(site__pk=choice_pk).exists()

            return filter(is_in_site, vlans)

    elif choice_type == 'vlan':
        vlan = get_object_or_404(Vlan, pk=choice_pk)

        def filter_network(present_pks):
            net_pks = vlan.network_set.all().values_list('pk', flat=True)
            net_pks = set(present_pks).intersection(set(net_pks))
            return pks_to_objs(net_pks, Network)

        def filter_site(present_pks):
            networks = vlan.network_set.filter(~Q(site=None))
            network_site_pks = networks.values_list('site', flat=True)
            site_pks = set(present_pks).intersection(set(network_site_pks))
            return pks_to_objs(site_pks, Site)

        def filter_vlan(present_pks):
            return [vlan]

    else:
        raise Exception("Not sure what to do here...")

    return filter_network, filter_site, filter_vlan


def label_value_maker():
    """
    We are going to need to put vlans, sites, networks, and ranges into the
    dom. This function makes functions that can make lists of JSON-able
    objects.
    """

    def format_network(networks):
        return list(
            {'label': n.network_str, 'value': n.pk} for n in networks
        )

    def format_site(sites):
        return list(
            {'label': s.full_name, 'value': s.pk} for s in sites
        )

    def format_vlan(vlans):
        return list(
            {'label': "{0}:{1}".format(v.name, v.number), 'value': v.pk}
            for v in vlans
        )
    return format_network, format_site, format_vlan


def calc_ranges(network):
    """
    Given a network, return the range information for that network. These
    ranges will be used by the user to decide where to request an IP address.
    This function will not actually find that ip address, it will mearly
    suggest which ranges a user might want to check in.

    Ranges will be constructed by two methods:

        1. A base template calculated from the netmask (number of addresses) in
        a network

        2. Inspecting the :class:`Range` objects associated with the network.

    This function should be allocation policy that netops controls.
    """
    # See https://mana.mozilla.org/wiki/display/NOC/Node+deployment for
    # allocation templates

    network.update_network()
    nbase = network.network.network
    name_fragment = calc_name_fragment(network)

    if network.prefixlen == 24:
        return [
            {
                'name': 'generic',
                'rtype': 'special purpose',
                'start': str(nbase + 1),
                'end': str(nbase + 15),
                'name_fragment': name_fragment
            },
            {
                'name': 'generic',
                'rtype': 'multi-host pools',
                'start': str(nbase + 16),
                'end': str(nbase + 127),
                'name_fragment': name_fragment
            },
            {
                'name': 'generic',
                'rtype': '/32 allocations',
                'start': str(nbase + 128),
                'end': str(nbase + 207),
                'name_fragment': name_fragment
            },
            {
                'name': 'generic',
                'rtype': 'load balancers',
                'start': str(nbase + 208),
                'end': str(nbase + 223),
                'name_fragment': name_fragment
            },
            {
                'name': 'generic',
                'rtype': 'dynamic',
                'start': str(nbase + 224),
                'end': str(nbase + 247),
                'name_fragment': name_fragment
            },
            {
                'name': 'generic',
                'rtype': 'dynamic',
                'start': str(nbase + 248),
                'end': str(nbase + 255),
                'name_fragment': name_fragment
            }
        ]
    else:
        return []


def calc_name_fragment(network, base_name=''):
    """
    Suggest some names given a network
    """
    if network.site:
        base_name = network.site.full_name

    if network.vlan:
        base_name = '.'.join([network.vlan.name, base_name])

    return base_name
