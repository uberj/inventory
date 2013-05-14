from core.registration.static.models import StaticReg

import hashlib

# This doesn't work for IPv6... yet


def render_statements(statements, **kwargs):
    return _render_kv(statements, **kwargs)


def render_options(options, **kwargs):
    return _render_kv(options, type_='option', **kwargs)


def _render_kv(kvs, type_='', tabs=1):
    build_str = ''
    if kvs:
        if type_:
            prefix = type_ + ' '  # The space is important!
        else:
            prefix = type_
        for kv in kvs:
            build_str += "{0}{1}{2:20} {3};\n".format(
                '\t' * tabs, prefix, kv.key.replace('_', '-'), kv.value
            )
        build_str += "\n"
    return build_str


def render_host(fqdn, ip_str, mac, i_n, options, statements, tabs=2):
    m = hashlib.md5()
    m.update(fqdn + ip_str + mac + i_n)
    digest = m.hexdigest()

    build_str = ''
    build_str += "{0}host {1}-{2} {{\n".format('\t' * (tabs - 1), fqdn, digest)
    build_str += "{0}hardware ethernet {1};\n".format('\t' * tabs, mac)
    build_str += "{0}fixed-address {1};\n".format('\t' * tabs, ip_str)
    build_str += render_statements(statements, tabs=tabs)
    build_str += render_options(options, tabs=tabs)
    build_str += "{0}}}\n\n".format('\t' * (tabs - 1))
    return build_str


def render_intr(intr, tabs=2):
    build_str = ''
    bis = intr.bondedintr_set.all()
    if bis.exists():
        for bi in bis:
            options = bi.keyvalue_set.filter(is_option=True)
            statements = bi.keyvalue_set.filter(is_statement=True)
            build_str += render_host(
                intr.fqdn, intr.ip_str, bi.mac, bi.interface_name, options,
                statements, tabs=tabs
            )
    else:
        if intr.mac == 'virtual':
            build_str += "# Mac was virtual"
            print "Bad!"
        else:
            options = intr.keyvalue_set.filter(is_option=True)
            statements = intr.keyvalue_set.filter(is_statement=True)
            build_str += render_host(
                intr.fqdn, intr.ip_str, intr.mac, intr.interface_name,
                options, statements, tabs=tabs
            )
    return build_str


def render_intrs(intrs):
    build_str = ''
    groups = {}
    for intr in intrs:
        if intr.group:
            # If this host belongs to a group we will render it, and any other
            # interface in the group, at a latter time.
            groups.setdefault(
                intr.group.name, (intr.group, [])
            )[1].append(intr)
        else:
            build_str += render_intr(intr)
    if groups:
        for group_name, (group, intrs) in groups.iteritems():
            build_str += "\tgroup {{  # group {0}\n\n".format(group_name)
            for intr in intrs:
                build_str += render_intr(intr, tabs=3)
            build_str += "\t}\n\n"

    return build_str


def build_subnet(network):
    """
    The core function of building DHCP files.

    :param network: The network that will be searched for
        :ref:`StaticReg` instances.
    :type network: :class:`StaticReg`
    """
    network_options = network.keyvalue_set.filter(is_option=True)
    network_statements = network.keyvalue_set.filter(is_statement=True)
    network_raw_include = network.dhcpd_raw_include
    # All interface objects that are within this network and have dhcp_enabled.
    # TODO, make this work with IPv6
    if network.ip_type == '6':
        raise NotImplemented()
    network.update_network()
    ip_lower_start = int(network.network.network)
    ip_lower_end = int(network.network.broadcast) - 1
    intrs = StaticReg.objects.filter(
        ip_upper=0,
        ip_lower__gte=ip_lower_start,
        ip_lower__lte=ip_lower_end,
        dhcp_enabled=True, ip_type='4'
    )
    ranges = network.range_set.all()

    # Let's assume all options need a ';' appended.
    build_str = "# Generated DHCP \n\n"
    build_str += "subnet {0} netmask {1} {{\n\n".format(
        network, network.network.netmask)
    build_str += "\t# Network Statements\n"
    build_str += render_statements(network_statements)
    build_str += "\t# Network Options\n"
    build_str += render_options(network_options)

    if network_raw_include:
        for line in network_raw_include.split('\n'):
            build_str += "\t{0}\n".format(line)
    build_str += "\n"

    for mrange in ranges:
        build_str += render_pool(mrange)

    build_str += render_intrs(intrs)

    build_str += "}"
    return build_str


def render_pool(mrange):
    pool_options = mrange.keyvalue_set.filter(is_option=True)
    pool_statements = mrange.keyvalue_set.filter(is_statement=True)

    build_str = "\tpool {\n"
    build_str += "\t\t# Pool Statements\n"
    build_str += render_statements(pool_statements, tabs=2)
    build_str += "\t\t# Pool Options\n"
    build_str += render_options(pool_options, tabs=2)
    build_str += "\n"

    if mrange.dhcpd_raw_include:
        build_str += "\t\t{0}\n".format(mrange.dhcpd_raw_include)

    build_str += "\t\trange {0} {1};\n".format(
        mrange.start_str, mrange.end_str
    )

    build_str += "\t}\n\n"
    return build_str
