import random
import string


def random_node():
    return ''.join([random.choice(string.uppercase) for _ in range(10)])


def build_link_graph(links, site=None):
    cache = {}
    graph = []
    for link in links:
        lc = cache.setdefault(link.a_site.full_name, 1)
        cache[link.a_site.full_name] = lc + 1
        graph.append({
            'source': link.a_site.full_name,
            'target': link.z_site.full_name,
            'type': 'root' if link.a_site == site else 'other',
            'lc': lc,
            'charge': -1000,
            'distance': 80,
            'fixed': True,
        })
        for n in filter(lambda n: n['source'] == link.a_site.full_name, graph):
            n['lm'] = lc
            #n['distance'] = min(70, (10 * lc))

    extras = []
    for link in graph:
        for i in range(10):
            extras.append({
                'target': link['source'],
                'source': random_node(),
                'type': 'ignore',
                'charge': -900,
                'lc': lc,
                'distance': link['distance'] + 10,
            })

    print graph
    return graph + extras
