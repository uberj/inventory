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
