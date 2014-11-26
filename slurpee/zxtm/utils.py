from core.search.compiler.django_compile import compile_to_django


def NodeProxy(object):
    """
    This class is meant to make all objects look similar enough so that the
    slurp script can operate on a common interface.
    """
    def __init__(self, system_hostname, otype, node):
        self.system_hostname = system_hostname
        self.otype = otype
        self.node = node

    def html(self, tig, pool, vserver):
        return (
            "This system has an {otype} that is tied to {node} which is "
            "backing TIG {tig} in the pool {pool}. Configuration is on the "
            "{vserver} vserver".format(
                node=self.node, tig=tig.name, pool=pool.name,
                vserver=vserver.name
            )
        )


def fqdn_ip_to_ids(fqdn_or_ip):
    ids = {}
    res, error = compile_to_django(fqdn_or_ip)
    for system in res['SYS']:
        for sreg in system.staticreg_set.all():
            ids.setdefault(sreg.ip_str, []).append(sreg.get_absolute_url())
            ids.setdefault(sreg.fqdn, []).append(sreg.get_absolute_url())

    for a in res['A']:
        ids.setdefault(a.ip_str, []).append((a.rdtype, a.get_absolute_url()))
        ids.setdefault(a.fqdn, []).append((a.rdtype, a.get_absolute_url()))

    for ptr in res['PTR']:
        ids.setdefault(ptr.name, []).append(
            (ptr.rdtype, ptr.get_absolute_url())
        )
        ids.setdefault(ptr.ip_str, []).append(
            (ptr.rdtype, ptr.get_absolute_url())
        )

    for sreg in res['SREG']:
        ids.setdefault(sreg.name, []).append(
            (sreg.rdtype, sreg.get_absolute_url())
        )
        ids.setdefault(ptr.ip_str, []).append(
            (sreg.rdtype, sreg.get_absolute_url())
        )

    return ids
