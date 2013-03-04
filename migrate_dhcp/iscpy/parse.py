from parsley import _GrammarWrapper as GrammarWrapper
from parsley import wrapGrammar
from copy import deepcopy

from django.core.exceptions import ValidationError

from core.network.models import Network
from core.range.models import Range
from migrate_dhcp.utils import migrate_host

import ipaddr
import sys
import re
import parsley
import pprint


pp = pprint.PrettyPrinter(indent=4)

def scrub_comments(in_str):
    new_str = ''
    index = 0
    while index < len(in_str):
        c = in_str[index]
        if c == '#':
            while True:
                index += 1
                if index >= len(in_str):
                    break
                if in_str[index] == '\n':
                    break
            continue # Back to top
        elif index < len(in_str) - 2 and c == '/' and in_str[index+1] == '*':
            while True:
                index += 2
                if (index < len(in_str) - 2 and
                        in_str[index] == '*' and in_str[index + 1] == '/'):
                    break
            index = index + 2  # skip close
            continue # Back to top
        new_str += c
        index += 1
    return new_str



ISC_GRAMMAR_FILE = "migrate_dhcp/isc.parsley"
grammar = open(ISC_GRAMMAR_FILE).read()
grammar += '\nS = stmt_list'

class CallBack(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self.func(*args)


class ISCGrammar(parsley.makeGrammar(grammar, {}, unwrap=True)):

    def __init__(self, *args, **kwargs):
        self.kwargs = deepcopy(kwargs)
        self.vlan_number = kwargs.pop('vlan_number')
        self.vlan_name = kwargs.pop('vlan_name')
        self.site_name = kwargs.pop('site_name')
        self.fname = kwargs.pop('fname')
        self.path_swap = (
            '/etc/dhcpconfig-autodeploy',
            '/home/juber/sysadmins/dhcpconfig/dhcpconfig-autodeploy/{0}'.format(self.site_name)
        )
        super(ISCGrammar, self).__init__(*args, **kwargs)

    def subnet(self, network_str, netmask, body):
        n_ = ipaddr.IPv4Network(network_str + '/' + netmask)
        n = Network.objects.filter(network_str=str(n_))
        if not n:
            n = Network(network_str=str(n_), ip_type='4')
            n.full_clean()
            n.save()
        else:
            n = n[0]
        kvs = self.process_opts_params(body, Network.keyvalue_set.related.model, n)
        callbacks = [ item for item in body if isinstance(item, CallBack) ]
        for callback in callbacks:
            print callback(n)
        print kvs
        return n

    nic_strip = re.compile("(.*)-(nic\d+)$")

    def host(self, hostname, options_params):
        m = self.nic_strip.match(hostname)
        if m:
            hostname = m.group(1)
            nic_name = m.group(2)
        else:
            import pdb;pdb.set_trace()

        kvs = []
        for op in options_params:
            if (len(op) > 2 and op[0] == 'parameter' and
                    op[1] == 'fixed-address'):
                ip_str = op[2]
                continue  # remove from kv store
            if (len(op) > 2 and op[0] == 'parameter' and
                    op[1] == 'hardware-ethernet'):
                mac = op[2]
                continue  # remove from kv store
            kvs.append(op)

        if not (ip_str and mac):
            print "Couldn't find mac and ip for {0}".format(hostname)
            return None

        return migrate_host(hostname, ip_str, mac, nic_name, kvs)

        print options_params
        return hostname, options_params

    def process_opts_params(self, stmts, KVClass, obj):
        """
        Walk through statements looking for 'parameter' and 'option' types.
        Return these as wrapped KV objects.
        """
        kvs = []
        for stmt in stmts:
            if not isinstance(stmt, tuple):
                continue
            if len(stmt) < 1:
                continue
            if stmt[0] in ('parameter', 'option'):
                try:
                    kv = KVClass(key=stmt[1].replace('-', '_'), value=stmt[2], obj=obj)
                    kv.clean(check_unique=False)  # This may change the format of the key
                    kv = KVClass.objects.get(
                        key=kv.key, value=kv.value, obj=obj
                    )
                except KVClass.DoesNotExist:
                    kv.clean()
                    kv.save()
                kvs.append(kv)
        return kvs

    def pool(self, stmts):
        """
        Pools are analogous to ranges. We first have to sort through the
        statements and find a the range parameter. If we don't find it, fail
        the migration.
        """
        def create_range(subnet):
            new_stmts = []
            start = end = None
            for stmt in stmts:
                if stmt[0:2] == ('parameter', 'range'):
                    start, end = stmt[2].split()
                    r = Range.objects.filter(start_str=start, end_str=end)
                    if not r:
                        r = Range(
                            start_str=start, end_str=end, ip_type='4',
                            network=subnet
                        )
                        r.clean()
                        r.save()
                    else:
                        r = r[0]

                else:
                    new_stmts.append(stmt)

            if not (start or end):
                raise

            kvs = self.process_opts_params(new_stmts, Range.keyvalue_set.related.model, r)
            return r, kvs

        return CallBack(create_range)


    def resolve_include(self, path):
        fname = path.replace(*self.path_swap)
        kwargs = deepcopy(self.kwargs)
        kwargs['fname'] = fname
        ret = _migrate(kwargs)
        return ret

def construct(scope={}):
    return wrapGrammar(ISCGrammar)

def parse(in_str, *args):
    in_str = scrub_comments(in_str)
    in_str = in_str.replace('\n', '').strip()
    g = construct()
    return g(in_str).S()

def parse_file(fname, *args):
    contents = open(fname).read()
    return parse(contents)

def migrate(args):
    kwargs = dict(
        [(k, v) for k, v
         in zip(('site_name', 'vlan_number', 'vlan_name', 'fname'), args)]
    )
    ret = _migrate(kwargs)
    pp.pprint(ret)

def _migrate(kwargs):

    # Get the contents of the file to be parse
    contents = open(kwargs['fname']).read()

    # Scrub the comments
    in_str = scrub_comments(contents)
    in_str = in_str.replace('\n', '').strip()

    # Build the parser
    g = GrammarWrapper(ISCGrammar(in_str, **kwargs), in_str)
    ret = g.S()
    return ret




def main(argv):
    fname = argv[1]
    print fname
    pp.pprint(parse_file(fname))

if __name__ == '__main__':
    main(sys.argv)
