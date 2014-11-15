import simplejson as json

from slurpee.zxtm.models import (
    Node as ORMNode,
    TIG as ORMTIG,
    Pool as ORMPool,
    VServer as ORMVServer,
    VServerListenOnTig
)

import sys
from jsonpointer import resolve_pointer


def log(msg, level='error'):
    if level == 'error':
        sys.stderr.write(str(msg) + '\n')


class PointerPath(object):
    rmap = {
        '/': '~1',
        ' ': '/ ',
        '~': '~0',
    }

    def __init__(self, path):
        new_path = []
        for c in path:
            new_path.append(self.rmap.get(c, c))
        self.path = ''.join(new_path)

    def __str__(self):
        return self.path

    def __add__(self, y):
        return self.path + y

    def __radd__(self, y):
        return y + self.path

    def __repr__(self):
        return "<PointerPath: {0}>".format(self.path)


class Pool(object):
    def __init__(self, name, blob):
        self.name = name
        self.blob = blob
        self.vservers = []

    def __str__(self):
        return self.blob.show_paths(prefix="{0}.".format(self.name))

    def __repr__(self):
        return str(self)

    @property
    def status(self):
        return self.blob.get_path('/status')

    @property
    def note(self):
        return self.blob.get_path('/note')

    @property
    def nodes_table(self):
        if not self.blob:
            return []
        return self.blob.get_path('/info/properties/basic').json['nodes_table']

    def make_orm_object(self):
        return ORMPool(name=self.name)


class TIG(object):
    def __init__(self, name, blob):
        self.name = name
        self.blob = blob
        self.vservers = []

    def __str__(self):
        return self.blob.show_paths(prefix="{0}.".format(self.name))

    def __repr__(self):
        return str(self)

    @property
    def status(self):
        return self.blob.get_path('/status')

    @property
    def note(self):
        return self.blob.get_path('/note')

    @property
    def ipaddresses(self):
        return self.blob.get_path('/info/properties/basic').json['ipaddresses']

    def make_orm_object(self):
        return ORMTIG(name=self.name)


class Nodes(object):
    """
    This is meant to be an inverted index of the ZuesState object that maps
    hosts to tigs, pools, and virtual servers.
    """
    def __init__(self, zstate):
        self._nodes = {}
        for pool in zstate.pools.values():
            for node in pool.nodes_table:
                node['node_id'] = node['node'].split(':')[0]
                self._process_node(node, pool)

    def _process_node(self, node_instance, pool):
        node_id = node_instance['node_id']
        if node_id not in self._nodes:
            new_node = Node(node_id=node_id)
            self._nodes[node_id] = new_node
        self._nodes[node_id].instances.append((pool, node_instance))

    def __iter__(self):
        def nodes():
            for node_name, node in self._nodes.iteritems():
                yield (node_name, node)
        return nodes()

    def save_orm_state(self):
        for node_name, node in self:
            log("Writing {0}".format(repr(node)))
            ORMNode.objects.bulk_create(node.make_orm_objects())


class Node(object):
    """
    Node is a representation of an IP or hostname. 10.1.1.1:500 10.1.1.1:501
    would be the *same* node.
    """
    def __init__(
        self, node_id=None
    ):
        self.node_id = node_id
        self.instances = []

    def __str__(self):
        pools = []
        for pool, instance in self.instances:
            pools.append(pool)
        return "node:{0} instances:{1}".format(
            self.node_id, ', '.join(p.name for p in pools)
        )

    def __repr__(self):
        return "<Node:{0}>".format(self)

    def make_orm_objects(self):
        for pool, instance in self.instances:
            yield ORMNode(
                node_id=self.node_id,
                name=instance['node'],
                pool=pool.name
            )


class ZXTM(object):
    def __init__(self, blob):
        self.blob = blob
        self._tigs = None
        self._pools = None
        self._vservers = None
        self._nodes = None

    def __str__(self):
        return str(self.blob)

    def __repr__(self):
        return str(self)

    @property
    def url(self):
        return self.blob.json['url']

    @property
    def nodes(self):
        if not self._nodes:
            self._nodes = Nodes(self)
        return self._nodes

    @property
    def tigs(self):
        if not self._tigs:
            self._tigs = {}
            for tig_name in self.blob.get_path('/tigs').json:
                if tig_name in self._tigs:
                    log(
                        "[WARNING] already seen tig with name {0}"
                        .format(tig_name)
                    )
                self._tigs[tig_name] = TIG(
                    tig_name,
                    self.blob.get_path('/tigs/' + tig_name)
                )
        return self._tigs

    @property
    def pools(self):
        if not self._pools:
            self._pools = {
                'discard': Pool(
                    'discard', None
                )
            }
            for pool_name in self.blob.get_path('/pools').json:
                if pool_name in self._pools:
                    print (
                        "[WARNING] already seen pool with name {0}"
                        .format(pool_name)
                    )
                self._pools[pool_name] = Pool(
                    pool_name, self.blob.get_path('/pools/' + pool_name)
                )
        return self._pools

    @property
    def vservers(self):
        if not self._vservers:
            self._vservers = {}
            for vserver_name in self.blob.get_path('/servers').json:
                if vserver_name in self._vservers:
                    log(
                        "[WARNING] already seen vserver with name {0}"
                        .format(vserver_name)
                    )
                self._vservers[vserver_name] = VServer(
                    vserver_name,
                    self.blob.get_path('/servers/' + vserver_name)
                )
        return self._vservers

    def orm_vservers_and_relationships(self):
        ORMVServers = []
        ORMVServers_TIG_relationships = []
        for vserver_name, vserver in self.vservers.iteritems():
            ORMVServers.append(vserver.make_orm_object())
            if vserver.pool_name not in self.pools:
                log("Parsing zxtm {0}".format(self.url))
                log("Couldn't find a pool for {0}".format(repr(vserver)))
            else:
                vserver.pool = self.pools[vserver.pool_name]
                self.pools[vserver.pool_name].vservers.append(vserver)

            for tig_name in vserver.listening_tigs:
                if not tig_name in self.tigs:
                    log("Parsing zxtm {0}".format(self.url))
                    log("Couldn't find a tig for {0}".format(repr(vserver)))
                else:
                    vserver.tigs.append(self.tigs[tig_name])
                    self.tigs[tig_name].vservers.append(vserver)
                    ORMVServers_TIG_relationships.append(
                        VServerListenOnTig(
                            vserver=vserver_name,
                            tig=tig_name
                        )
                    )
        return ORMVServers, ORMVServers_TIG_relationships

    def orm_pools(self):
        """
        Make Django ORM objects that can be saved to the database.
        """
        for pool in self.pools.values():
            log("Writing Pool {0}".format(pool.name))
            yield pool.make_orm_object()

    def orm_tigs(self):
        """
        Make Django ORM objects that can be saved to the database.
        """
        for tig in self.tigs.values():
            log("Writing TIG {0}".format(tig.name))
            yield tig.make_orm_object()

    def save_orm_state(self):
        ORMPool.objects.bulk_create(self.orm_pools())
        ORMTIG.objects.bulk_create(self.orm_tigs())
        orm_vservers, orm_vserver_relationships = (
            self.orm_vservers_and_relationships()
        )
        ORMVServer.objects.bulk_create(orm_vservers)
        VServerListenOnTig.objects.bulk_create(orm_vserver_relationships)

        nodes = Nodes(self)
        nodes.save_orm_state()


class VServer(object):
    def __init__(self, name, blob):
        self.name = name
        self.blob = blob
        self.tigs = []

    def __str__(self):
        return self.blob.show_paths(prefix="{0}.".format(self.name))

    def __repr__(self):
        return "<VServer: name={0} pool={1} tigs={2}>".format(
            self.name, self.pool_name, ','.join(tig.name for tig in self.tigs)
        )

    @property
    def pool_name(self):
        return self.blob.get_path('/info/properties/basic').json[
            'pool'
        ]

    @property
    def listening_tigs(self):
        return self.blob.get_path('/info/properties/basic').json[
            'listen_on_traffic_ips'
        ]

    def make_orm_object(self):
        return ORMVServer(name=self.name, pool=self.pool_name)


class Blob(object):
    def __init__(self, json_blob):
        self.json_blob = json_blob

    def __str__(self):
        return self.show_paths()

    def __repr__(self):
        return str(self)

    @property
    def json(self):
        return self.json_blob

    def get_path(self, path):
        try:
            return Blob(resolve_pointer(self.json_blob, path))
        except KeyError:
            raise KeyError("[ERROR] couldn't parse {0}".format(path))

    def show_paths(self, prefix=''):
        return '\n'.join(self.list_paths(prefix))

    def list_paths(self, prefix):
        return self._list_path(prefix, self.json_blob)

    def list_path(self, path, prefix=''):
        blob = self.get_path(path)
        return self._list_path(prefix, blob.json)

    def _list_path(self, prefix, json_blob):
        if isinstance(json_blob, list):
            return json_blob

        result = []
        more = []
        for key, value in json_blob.iteritems():
            if isinstance(value, dict):
                more += self._list_path(prefix + key + '.', value)
            elif isinstance(value, list):
                for cn in value:
                    more += self._list_path(prefix, {key: cn})
            else:
                result.append("{0}{1} = {2}".format(prefix, key, value))
        return result + more


class ZXTMState(object):
    def __init__(self, ulr=None, filename=None, version='0.005'):
        with open(filename, 'r') as fd:
            self.blob = Blob(json.load(fd))

        if self.version != version:
            log("Version mismatch!")

    @property
    def version(self):
        return self.blob.json['version']

    @property
    def zxtms(self):
        for zxtm in iter(zxtm for zxtm in self.blob.json['zxtms']):
            ppath = '/zxtms/' + PointerPath(zxtm)
            yield ZXTM(self.blob.get_path(ppath))

    def save_orm_state(self):
        for zxtm in self.zxtms:
            zxtm.save_orm_state()

    @classmethod
    def clear_orm_state(cls):
        ORMPool.objects.all().delete()
        ORMTIG.objects.all().delete()
        ORMVServer.objects.all().delete()
        VServerListenOnTig.objects.all().delete()


class AllNodes(ZXTMState):
    def __init__(self, zs):
        self.zs = zs

    def find(self, node_id):
        for zxtm in self.zs.zxtms:
            try:
                return zxtm.nodes[node_id]
            except KeyError:
                continue
        raise KeyError("No node {0}".format(node_id))

    def __iter__(self):
        for zxtm in self.zs.zxtms:
            for node in zxtm.nodes:
                yield node


if __name__ == '__main__':
    zs = ZXTMState(filename='zxtm.json')
    if False:
        for zxtm in zs.zxtms:
            for pool_name, pool in zxtm.pools.iteritems():
                print '-' * 50
                print 'Name: ' + pool_name
                print pool
            for vserver_name, vserver in zxtm.vservers.iteritems():
                print '-' * 50
                print 'Name: ' + vserver.name
                print vserver
            for tig_name, tig in zxtm.tigs.iteritems():
                print '-' * 50
                print 'Name: ' + tig_name
                print tig.ipaddresses
            for node in zxtm.nodes:
                print '-' * 50
                print node
    allnodes = AllNodes(zs)
    host_id = '10.20.77.22'
    node = allnodes.find(host_id)
    print "Looking up info for {0}".format(host_id)
    print ""
    for node, pool in node.instances:
        for vserver in pool.vservers:
            for tig in vserver.tigs:
                print (
                    "Node {node} is backing TIG {tig} in the pool {pool}. "
                    "Configuration is on the {vserver} vserver".format(
                        node=node['node'], tig=tig.name, pool=pool.name,
                        vserver=vserver.name
                    )
                )
