from core.search.compiler.django_compile import compile_to_django

def NodeProxy(object):
    """
    This class is meant to make all objects look similar enough so that the
    slurp script can operate on a common interface.
    """
    def __init__(self, system_hostname, otype, node):
        self.system_hostname = hostname
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

def fqdn_to_ids(hostname):
    """
    Take a hostname and do all the magic to find all the ips/hostnames
    associated with a given hostname.

    How this function works:
        * First any system objects with matching host names are looked at.
            - If there are sreg objects, those ip addresses are added to the
              pool
        * A recoreds are checked
        * PTR records are checked
    """
    ids = set()
    res, error = compile_to_django(hostname)
    for system in res['SYS']:
        for sreg in system.staticreg_set.all():
            ids.add(sreg.ip_str)
            ids.add(sreg.fqdn)

    for a in res['A']:
        ids.add(a.ip_str)
        ids.add(a.fqdn)

    for ptr in res['ptr']:
        ids.add(ptr.ip_str)
        ids.add(ptr.name)

    return ids
